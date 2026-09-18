---
id: dotnet.architecture.ddd
title: Domain-Driven Design
category: skill
domain: dotnet
technologies: [dotnet]
triggers: [domain driven design, ddd, aggregate, bounded context, value object, entity modeling, ubiquitous language]
requires: []
related: [dotnet.architecture.clean-architecture, dotnet.architecture.modular-monolith, dotnet.architecture.domain-events-outbox]
optional: []
prerequisites: []
tags: [architecture, domain-modeling]
---

# Domain-Driven Design

## Purpose
Model software around the actual business domain and its language, so the
code structure mirrors how domain experts think about the problem, and
complex business rules have one clear home.

## When to Use
- The domain has real complexity: invariants, workflows, state transitions
  that matter to the business.
- Multiple bounded contexts with different meanings for the same term (e.g.
  "Customer" means something different in Billing vs. Support).
- Not for simple data-shuffling CRUD — see Anti-Patterns.

## Prerequisites
`dotnet.architecture.clean-architecture` for where domain code lives
relative to infrastructure.

## Inputs Required
Actual domain rules from the requirement or domain expert — never invent an
invariant that wasn't stated or clearly implied.

## Engineering Principles
1. Ubiquitous language: code names match the language the business actually
   uses, not a generic technical vocabulary.
2. Entities have identity and a lifecycle; value objects are immutable and
   compared by value.
3. Aggregates enforce invariants across a cluster of objects and are the
   unit of consistency — one aggregate, one transaction.
4. Bounded contexts have their own model of a shared concept; don't force
   one universal model across contexts.
5. Domain logic lives in entities/value objects/domain services, not in
   application services (avoid anemic domain models).

## Step-by-Step Workflow
1. Identify bounded contexts from the requirement — where does the meaning
   of a term change across the system?
2. Within a context, identify aggregates: what must stay consistent
   together, and what's the aggregate root that enforces that.
3. Model value objects for anything defined by its attributes, not identity
   (money, address, email, date range).
4. Put invariant checks inside the aggregate (constructors/methods), not in
   the application layer calling it.
5. Use domain events for side effects that other aggregates/contexts care
   about (see `dotnet.architecture.domain-events-outbox`).

## Code Standards
- Value objects are immutable `record`/`readonly struct` types with
  validation in the constructor/factory.
- Aggregate roots expose behavior methods (`order.Cancel()`), not public
  setters that let external code put them in an invalid state.
- Private/internal setters on entity collections; mutate through methods.

## Architecture Constraints
An aggregate is loaded and saved as a whole through its repository — no
reaching into another aggregate's internals from outside it. Cross-aggregate
consistency is eventual, coordinated via domain/integration events, not a
shared transaction spanning aggregates.

## Security Considerations
Invariant enforcement inside the aggregate is itself a security control —
e.g. an `Order` that refuses a negative quantity can't be forced into an
invalid state through a bypassed API validation layer.

## Testing Requirements
Unit test aggregates directly (no database) for every invariant: valid
transitions succeed, invalid ones are rejected with a clear reason.

## Common Mistakes
- Anemic domain model: entities are data bags; all logic lives in services.
- One giant aggregate covering the whole object graph, causing contention
  and awkward transactions.
- Reusing the same "Customer" entity verbatim across unrelated bounded
  contexts instead of letting each context model what it actually needs.

## Anti-Patterns
- **CRUD-driven domain**: modeling entities to match database tables instead
  of business behavior.
- **Aggregate soup**: aggregates referencing each other's internals directly
  instead of by identity reference.
- **DDD for a simple CRUD app**: applying full tactical DDD to a service
  with no real invariants — pure ceremony, see `rules/architecture.md`.

## Validation Checklist
- [ ] Every invariant is enforced inside the aggregate, not in a caller.
- [ ] Value objects are immutable and validate on construction.
- [ ] Aggregate boundaries match actual transactional consistency needs.
- [ ] Cross-aggregate effects go through domain events, not direct calls.

## Definition of Done
Meets `rules/definition-of-done.md`; every new invariant has a unit test
proving both the valid and invalid case.

## Example
```csharp
public sealed record Money(decimal Amount, string Currency)
{
    public Money
    {
        if (Amount < 0) throw new ArgumentException("Amount cannot be negative.");
        if (string.IsNullOrWhiteSpace(Currency)) throw new ArgumentException("Currency required.");
    }

    public static Money operator +(Money a, Money b)
    {
        if (a.Currency != b.Currency)
            throw new InvalidOperationException("Currency mismatch.");
        return a with { Amount = a.Amount + b.Amount };
    }
}

public sealed class Order
{
    private readonly List<OrderLine> _lines = new();
    public OrderId Id { get; }
    public OrderStatus Status { get; private set; } = OrderStatus.Draft;

    public Result Submit()
    {
        if (_lines.Count == 0)
            return Result.Failure("Cannot submit an order with no lines.");
        if (Status != OrderStatus.Draft)
            return Result.Failure($"Cannot submit an order in status {Status}.");

        Status = OrderStatus.Submitted;
        return Result.Success();
    }
}
```
The invariant ("no empty order can be submitted") lives inside `Order`, not
in the handler calling it — any caller gets the same protection.

## Related Skills
- `dotnet.architecture.clean-architecture` — layering that keeps this domain
  model free of infrastructure concerns.
- `dotnet.architecture.domain-events-outbox` — propagating aggregate state
  changes to other aggregates/contexts reliably.
- `dotnet.architecture.modular-monolith` — how bounded contexts map to
  module boundaries in a single deployable.
