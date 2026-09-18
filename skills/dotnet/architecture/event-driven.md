---
id: dotnet.architecture.event-driven
title: Event-Driven Architecture
category: skill
domain: dotnet
technologies: [dotnet, messaging]
triggers: [event driven, pub sub, event bus, integration events, domain events]
requires: []
related: [dotnet.architecture.domain-events-outbox, dotnet.messaging, dotnet.architecture.microservices]
optional: []
prerequisites: []
tags: [architecture, events]
---

# Event-Driven Architecture

## Purpose
Decouple producers from consumers by communicating through events —
facts about something that happened — instead of direct calls, enabling
independent evolution and asynchronous processing.

## When to Use
- Multiple consumers care about the same fact and shouldn't be coupled to
  the producer's call graph.
- Processing can happen asynchronously without the caller waiting.
- Not for a simple request/response where the caller needs an immediate,
  synchronous answer.

## Prerequisites
None beyond basic messaging concepts.

## Inputs Required
Whether consumers genuinely need decoupling/async processing, or whether a
direct call is simpler and sufficient (`rules/architecture.md`).

## Engineering Principles
1. Distinguish domain events (in-process, within one transaction/aggregate
   boundary) from integration events (cross-process/cross-service, published
   after the transaction commits) — see
   `dotnet.architecture.domain-events-outbox`.
2. Events are facts, named in the past tense (`OrderSubmitted`, not
   `SubmitOrder`) — a command is an instruction, an event is a fact.
3. Consumers are independent — a slow or failing consumer must not block
   the producer or other consumers.
4. Events carry enough data for common consumers to act without an
   immediate callback to the producer, but avoid turning every event into a
   full entity snapshot — version the schema deliberately.

## Step-by-Step Workflow
1. Identify the fact worth publishing and who needs to know.
2. Choose domain event (in-process, same transaction) vs. integration event
   (published after commit, crosses process boundary).
3. Define the event schema — versioned, minimal but sufficient for known
   consumers.
4. Publish reliably: for integration events, use the outbox pattern
   (`dotnet.architecture.domain-events-outbox`) rather than publish-then-
   commit, which can lose events on failure.
5. Consumers process idempotently — the same event may be delivered more
   than once under at-least-once delivery.

## Code Standards
Event types are immutable records with a version/schema identifier if the
event contract is expected to evolve.

## Architecture Constraints
Producers never depend on a specific consumer's existence or behavior — the
event contract is the only coupling point.

## Security Considerations
Events crossing a trust boundary (cross-service, cross-tenant) must not
carry more data than the consumer is authorized to see — treat the event
payload like any other cross-boundary contract (`dotnet.security`).

## Testing Requirements
Test that an event is published on the expected state change, and that
consumers handle duplicate delivery and out-of-order arrival correctly
where the transport doesn't guarantee ordering.

## Common Mistakes
- Publishing before the transaction commits, so a rolled-back transaction
  still emits an event that never actually happened.
- Consumers assuming exactly-once, in-order delivery from a transport that
  only guarantees at-least-once.

## Anti-Patterns
- **Event-driven everything**: replacing every direct call with an event,
  including ones needing an immediate synchronous answer — adds latency and
  complexity with no benefit.
- **Fat events**: publishing an entire aggregate snapshot on every change
  "just in case," coupling every consumer to the full internal shape.

## Validation Checklist
- [ ] Domain vs. integration event distinction is deliberate.
- [ ] Integration events are published via outbox, not publish-then-commit.
- [ ] Consumers are idempotent.
- [ ] Event schema is versioned if consumers are external/independently
      deployed.

## Definition of Done
Meets `rules/definition-of-done.md`; new event has a test proving it's
published on the correct state transition and not on a rolled-back one.

## Example
```csharp
public sealed record OrderSubmitted(Guid OrderId, DateTimeOffset SubmittedAtUtc, int SchemaVersion = 1);

// Published via outbox after the transaction that submitted the order commits —
// never published inline before SaveChangesAsync succeeds.
```

## Related Skills
- `dotnet.architecture.domain-events-outbox` — reliable publication detail.
- `dotnet.messaging` — transport-level concerns (broker choice, delivery
  guarantees).
- `dotnet.architecture.microservices` — common consumer of integration
  events across service boundaries.
