---
id: dotnet.architecture.domain-events-outbox
title: Domain Events & Outbox Pattern
category: skill
domain: dotnet
technologies: [dotnet, efcore]
triggers: [domain events, outbox pattern, reliable event publishing, transactional messaging]
requires: [dotnet.efcore]
related: [dotnet.architecture.ddd, dotnet.architecture.event-driven, dotnet.messaging]
optional: []
prerequisites: [dotnet.architecture.ddd]
tags: [architecture, events, reliability]
---

# Domain Events & Outbox Pattern

## Purpose
Raise domain events inside an aggregate as part of a business operation,
and publish the resulting integration events reliably — exactly once from
the application's perspective — even if the process crashes between
committing the database transaction and publishing to the message broker.

## When to Use
- An aggregate's state change needs to trigger effects in other aggregates/
  modules/services.
- The publish must not be lost if the process dies right after the database
  commit (i.e., "publish or don't commit" isn't good enough — you need
  "commit and publish are effectively atomic").

## Prerequisites
`dotnet.architecture.ddd` (domain events raised by aggregates),
`dotnet.efcore` (transactional write to the outbox table).

## Inputs Required
Which state changes need reliable downstream notification, and which
consumers (in-process handlers vs. cross-process integration events).

## Engineering Principles
1. An aggregate raises domain events as part of its business method (e.g.
   `order.Submit()` raises `OrderSubmitted`) — it doesn't publish them
   itself.
2. Domain events are dispatched in-process, within the same transaction,
   to any in-process handlers (e.g. updating a read model).
3. Integration events (things other services/modules need to know) are
   written to an outbox table in the *same* database transaction as the
   aggregate's state change — this is what makes publishing atomic with the
   state change.
4. A separate background process reads the outbox and publishes to the
   actual message broker, marking rows as sent — retrying on failure,
   guaranteeing at-least-once delivery to the broker.
5. Consumers of integration events must be idempotent (at-least-once, not
   exactly-once, is what this pattern guarantees end-to-end).

## Step-by-Step Workflow
1. Aggregate raises domain event(s) via a protected method
   (`AddDomainEvent`), stored on the aggregate until dispatched.
2. Before `SaveChangesAsync`, the `DbContext` (or an interceptor) collects
   raised events from tracked aggregates.
3. In-process domain event handlers run synchronously within the same unit
   of work (or immediately after, still within the transaction, depending
   on consistency needs).
4. For events needing cross-process delivery, write a row to an
   `OutboxMessages` table in the same `SaveChangesAsync` call.
5. A background worker (`dotnet.dotnet` — `BackgroundService`) polls
   `OutboxMessages` for unsent rows, publishes them to the broker, and marks
   them sent — with retry and idempotency (message id) on the publish side.

## Code Standards
Outbox rows store: id, event type, JSON payload, created-at, sent-at
(nullable), and enough metadata (correlation id) for tracing. The publisher
worker is idempotent: publishing the same row twice must be safe for
consumers (they dedupe by message id).

## Architecture Constraints
The aggregate never calls the message broker directly — only the outbox
table, written in the same transaction as the state change. The broker
publish step is entirely decoupled from the request that caused it.

## Security Considerations
Outbox payloads follow the same cross-boundary data rules as any published
event (`dotnet.architecture.event-driven` — don't leak unauthorized data).

## Testing Requirements
Integration test: committing an aggregate change writes the expected outbox
row in the same transaction; a rolled-back transaction writes no row.
Test the publisher worker's idempotency (re-processing a row already
marked sent is a no-op or safely re-publishes without duplicate side
effects at the consumer).

## Common Mistakes
- Publishing to the broker directly inside the request handler, after
  `SaveChangesAsync` — a crash between the two loses the event with no
  way to recover it. This is exactly what the outbox avoids.
- Forgetting to make the outbox write part of the *same* transaction as the
  aggregate change (e.g. a separate `SaveChangesAsync` call) — reintroduces
  the same atomicity gap.

## Anti-Patterns
- **Outbox for everything**: writing every in-process domain event to the
  outbox even when no other process/service needs to know — adds latency
  and infrastructure for no benefit; use in-process dispatch for purely
  local effects.
- **Missing idempotency downstream**: relying on the outbox for reliability
  but writing consumers that break on duplicate delivery.

## Validation Checklist
- [ ] Integration events are written to the outbox in the same transaction
      as the aggregate change.
- [ ] The publisher worker retries failed publishes and doesn't lose rows.
- [ ] Consumers are idempotent against duplicate delivery.

## Definition of Done
Meets `rules/definition-of-done.md`; a test proves the outbox row is only
committed alongside a successful aggregate change, never independently.

## Example
```csharp
public abstract class AggregateRoot
{
    private readonly List<object> _domainEvents = new();
    public IReadOnlyList<object> DomainEvents => _domainEvents;
    protected void AddDomainEvent(object domainEvent) => _domainEvents.Add(domainEvent);
    public void ClearDomainEvents() => _domainEvents.Clear();
}

// In SaveChangesAsync override / interceptor:
public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
{
    var aggregatesWithEvents = ChangeTracker.Entries<AggregateRoot>()
        .Select(e => e.Entity)
        .Where(a => a.DomainEvents.Count > 0)
        .ToList();

    foreach (var aggregate in aggregatesWithEvents)
        foreach (var domainEvent in aggregate.DomainEvents)
            OutboxMessages.Add(OutboxMessage.From(domainEvent)); // same transaction

    var result = await base.SaveChangesAsync(ct);
    aggregatesWithEvents.ForEach(a => a.ClearDomainEvents());
    return result;
}
```

## Related Skills
- `dotnet.architecture.ddd` — where domain events originate.
- `dotnet.architecture.event-driven` — event design principles.
- `dotnet.messaging` — the broker the outbox publisher writes to.
