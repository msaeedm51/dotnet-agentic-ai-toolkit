---
id: dotnet.architecture.repository-specification
title: Repository & Specification Patterns
category: skill
domain: dotnet
technologies: [dotnet, efcore]
triggers: [repository pattern, specification pattern, abstract data access, query object]
requires: []
related: [dotnet.architecture.clean-architecture, dotnet.efcore]
optional: []
prerequisites: []
tags: [architecture, data-access]
---

# Repository & Specification Patterns

## Purpose
Give the domain/application layer a persistence-agnostic way to load and
save aggregates (Repository), and a composable, testable way to express
query criteria (Specification) without leaking `IQueryable`/EF Core
concerns into the domain.

## When to Use
- Clean Architecture with a domain layer that must not reference EF Core.
- Query criteria that's reused across multiple call sites and worth naming.
- Not needed for pure CQRS read-side queries that project straight to a DTO
  — those can use EF Core/Dapper directly in the query handler (see
  `dotnet.architecture.cqrs`); the repository pattern is for the write side
  (aggregate loading) and reusable query criteria.

## Prerequisites
`dotnet.architecture.clean-architecture`.

## Inputs Required
Which aggregates need a repository (write-side, loaded/saved as a whole),
and which query criteria are actually reused enough to warrant a named
specification.

## Engineering Principles
1. Repository interfaces live in Application/Domain; implementations live
   in Infrastructure.
2. A repository operates on one aggregate root, loaded/saved as a whole —
   not a generic `IRepository<T>` over every entity type, which encourages
   reaching into aggregate internals.
3. Specifications encapsulate a reusable query predicate (and optionally
   includes/ordering) as a named, testable object instead of inline LINQ
   scattered across call sites.
4. Don't expose `IQueryable` from the repository interface — that leaks the
   ORM's query capability into the domain/application layer and defeats the
   abstraction.

## Step-by-Step Workflow
1. Define a repository interface per aggregate root with the specific
   operations actually needed (`FindAsync`, `SaveAsync`) — not a generic
   CRUD-everything interface.
2. Implement it in Infrastructure using EF Core, translating specifications
   to `IQueryable` internally.
3. For reused query criteria, define a `Specification<T>` with a predicate
   (and optional includes) that the repository can apply.
4. Keep specification composition simple — `And`/`Or` combinators only if
   actually needed; don't build a general-purpose query DSL speculatively.

## Code Standards
Repository method names describe intent (`FindActiveByCustomerAsync`), not
generic CRUD verbs layered with generic type parameters.

## Architecture Constraints
Repository interfaces belong to Application/Domain; only the implementation
references EF Core. No `DbContext` type appears in a domain-layer interface
signature.

## Security Considerations
Specifications that take user input as query criteria must validate/
constrain that input (e.g. page size limits) to avoid unbounded queries
from becoming a denial-of-service vector.

## Testing Requirements
Unit test specifications against an in-memory collection or a real database
fixture to confirm the predicate matches intent; integration-test the EF
Core implementation against a real database for translation correctness (
LINQ that doesn't translate to SQL fails at runtime, not compile time).

## Common Mistakes
- A generic `IRepository<T>` for every entity, encouraging code to query
  entities that should only be reached through their aggregate root.
- Specifications that grow into a full ad hoc query builder instead of
  staying focused on reused, named criteria.

## Anti-Patterns
- **Repository over IQueryable**: `IRepository<T> { IQueryable<T> Query(); }`
  — this doesn't abstract EF Core at all, it just adds an indirection layer
  around it.
- **Specification for everything**: wrapping a one-off query used in exactly
  one place in a named specification class for no reuse benefit.

## Validation Checklist
- [ ] Repository interfaces are per-aggregate, not generic-over-everything.
- [ ] No `IQueryable` or `DbContext` type crosses into Domain/Application.
- [ ] Specifications used more than once are named and tested.

## Definition of Done
Meets `rules/definition-of-done.md`; new specification has a test proving
the predicate matches the intended records and excludes others.

## Example
```csharp
// Application/Domain — no EF Core reference
public interface IOrderRepository
{
    Task<Order?> FindAsync(OrderId id, CancellationToken ct);
    Task<IReadOnlyList<Order>> FindAsync(Specification<Order> spec, CancellationToken ct);
    Task SaveAsync(Order order, CancellationToken ct);
}

public sealed class OverdueOrdersSpecification : Specification<Order>
{
    public override Expression<Func<Order, bool>> ToExpression() =>
        o => o.Status == OrderStatus.Submitted && o.SubmittedAtUtc < DateTimeOffset.UtcNow.AddDays(-3);
}

// Infrastructure — translates the specification to EF Core
public sealed class EfOrderRepository(AppDbContext db) : IOrderRepository
{
    public async Task<IReadOnlyList<Order>> FindAsync(Specification<Order> spec, CancellationToken ct) =>
        await db.Orders.Where(spec.ToExpression()).ToListAsync(ct);

    public Task<Order?> FindAsync(OrderId id, CancellationToken ct) =>
        db.Orders.FirstOrDefaultAsync(o => o.Id == id, ct);

    public Task SaveAsync(Order order, CancellationToken ct) => db.SaveChangesAsync(ct);
}
```

## Related Skills
- `dotnet.architecture.clean-architecture` — layering this pattern sits
  inside.
- `dotnet.efcore` — translation/performance detail for the implementation.
