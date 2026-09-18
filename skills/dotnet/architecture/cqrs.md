---
id: dotnet.architecture.cqrs
title: CQRS (Command Query Responsibility Segregation)
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore]
triggers: [cqrs, command query separation, mediatr, separate reads and writes]
requires: []
related: [dotnet.architecture.clean-architecture, dotnet.architecture.result-rop, dotnet.database]
optional: []
prerequisites: [dotnet.architecture.clean-architecture]
tags: [architecture, cqrs]
---

# CQRS (Command Query Responsibility Segregation)

## Purpose
Separate the model used to write data (commands) from the model used to
read it (queries), so each can be optimized and evolved independently.

## When to Use
- Read and write models genuinely diverge (complex writes with invariants,
  simple flat reads for display) or have very different scaling needs.
- Not required to justify a separate database per side — that's a further,
  optional step (CQRS with separate read store), not the default.
- Skip entirely for a simple CRUD resource where one model serves both —
  see Anti-Patterns.

## Prerequisites
`dotnet.architecture.clean-architecture` for where handlers live.

## Inputs Required
Whether read and write models actually diverge enough to justify the split;
if they don't, don't force it (`rules/architecture.md`).

## Engineering Principles
1. Commands express intent and change state; they don't return domain data
   beyond an id/result.
2. Queries never change state and can bypass the domain model entirely,
   reading straight to a DTO-shaped projection.
3. One handler per command/query — no god-service handling many operations.
4. Commands go through domain invariants (aggregates); queries don't need to.

## Step-by-Step Workflow
1. Identify the operation as a command (changes state) or query (reads
   state) — don't mix the two in one handler.
2. For commands: route through the domain/aggregate, enforce invariants,
   persist via the write model.
3. For queries: project directly to a read DTO — using EF Core
   `AsNoTracking()` + `Select`, Dapper, or a dedicated read store — skip
   loading full aggregates just to read a few fields.
4. Wire both into the API layer via DTOs, never domain entities.

## Code Standards
- Command/query types are immutable records named `<Verb><Noun>Command` /
  `<Noun>By<Criteria>Query`.
- Query handlers use `AsNoTracking()` in EF Core; never track entities for
  read-only paths.

## Architecture Constraints
Query handlers must not call into command handlers or mutate state.
Commands should not return large read projections — return an id or a
minimal result; fetch details via a separate query if the caller needs them.

## Security Considerations
Authorize commands and queries independently — a user allowed to view a
resource is not automatically allowed to modify it. Enforce both at the
handler or endpoint boundary (`dotnet.authorization`).

## Testing Requirements
Unit test command handlers against the domain (invariant enforcement);
integration-test query handlers against a real database for projection
correctness and query shape (N+1 detection).

## Common Mistakes
- A "query" that also updates a `LastAccessed` timestamp — silently makes it
  a command; be explicit about side effects.
- Reusing the write-side aggregate for read projections, causing
  unnecessary tracking overhead and over-fetching.

## Anti-Patterns
- **CQRS everywhere**: introducing command/query separation on a trivial
  CRUD resource with no divergence — pure ceremony.
- **Separate database per side by default**: adding eventual-consistency
  complexity (a second data store, sync mechanism) without a concrete
  scaling or read-shape requirement driving it.

## Validation Checklist
- [ ] Commands don't return large data shapes; queries don't mutate state.
- [ ] Query handlers use no-tracking reads.
- [ ] Each handler is authorized independently.

## Definition of Done
Meets `rules/definition-of-done.md`; command handlers have unit tests
against domain invariants, query handlers have integration tests against a
real database.

## Example
```csharp
public sealed record SubmitOrderCommand(OrderId OrderId);

public sealed class SubmitOrderHandler(IOrderRepository repository)
{
    public async Task<Result> Handle(SubmitOrderCommand cmd, CancellationToken ct)
    {
        var order = await repository.FindAsync(cmd.OrderId, ct);
        if (order is null) return Result.Failure("Order not found.");

        var result = order.Submit();
        if (result.IsSuccess) await repository.SaveAsync(order, ct);
        return result;
    }
}

public sealed record OrderSummary(Guid Id, string Status, decimal Total);

public sealed class GetOrderSummaryHandler(AppDbContext db)
{
    public Task<OrderSummary?> Handle(Guid orderId, CancellationToken ct) =>
        db.Orders.AsNoTracking()
            .Where(o => o.Id == orderId)
            .Select(o => new OrderSummary(o.Id, o.Status.ToString(), o.Total))
            .FirstOrDefaultAsync(ct);
}
```

## Related Skills
- `dotnet.architecture.clean-architecture` — where command/query handlers
  live relative to domain and infrastructure.
- `dotnet.architecture.result-rop` — `Result` used for command outcomes.
- `dotnet.database` — no-tracking query projection detail.
