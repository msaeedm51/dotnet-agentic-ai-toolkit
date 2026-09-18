---
id: dotnet.architecture.clean-architecture
title: Clean Architecture
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore]
triggers: [clean architecture, layered architecture, onion architecture, dependency inversion, separate domain from infrastructure]
requires: []
related: [dotnet.architecture.ddd, dotnet.architecture.result-rop, dotnet.architecture.repository-specification]
optional: []
prerequisites: []
tags: [architecture, layering]
---

# Clean Architecture

## Purpose
Keep business logic independent of frameworks, UI, and infrastructure so it
can be tested, changed, and reasoned about without dragging in ASP.NET Core,
EF Core, or any specific database or external service.

## When to Use
- A project with business rules worth protecting from framework churn.
- Multiple entry points (API + background worker + CLI) sharing the same
  domain logic.
- Not for a thin CRUD service with no real business logic — see Anti-Patterns.

## Prerequisites
Basic dependency injection and interface-based design in C#.

## Inputs Required
- The actual business rules/invariants (from the requirement, not invented).
- Which infrastructure concerns exist (database, external APIs, messaging).

## Engineering Principles
1. Dependencies point inward: Infrastructure → Application → Domain. Domain
   depends on nothing.
2. The domain layer has no reference to ASP.NET Core, EF Core, or any
   specific infrastructure package.
3. Application layer defines interfaces (ports); Infrastructure implements
   them (adapters).
4. Presentation (API/UI) depends on Application, never directly on
   Infrastructure or Domain internals beyond what Application exposes.
5. Cross the boundary with DTOs/contracts, not domain entities (see
   `dotnet.api-design`).

## Step-by-Step Workflow
1. Identify the domain: entities, value objects, invariants, domain
   services — no persistence or framework concerns here.
2. Define application use cases (commands/queries or application services)
   that orchestrate domain logic and call out to ports (interfaces) for
   anything external.
3. Implement infrastructure adapters (EF Core repositories, HTTP clients,
   messaging) behind those ports.
4. Wire dependency injection in the composition root (typically
   `Program.cs`) — this is the only place that knows about every layer.
5. Expose use cases through the presentation layer (API/minimal endpoints)
   using DTOs, never domain entities.

## Code Standards
- Project references enforce the dependency direction: `Domain` has zero
  project references; `Application` references `Domain`; `Infrastructure`
  references `Application`; `Api`/`Presentation` references `Application`
  and `Infrastructure` only at the composition root.
- No `using Microsoft.EntityFrameworkCore` (or any infra package) inside
  `Domain` or `Application` project files.

## Architecture Constraints
- Enforce dependency direction with an architecture test (see
  `dotnet.testing`) — do not rely on code review alone to catch a violation.
- Domain entities never implement infrastructure interfaces (e.g.
  `IEntityTypeConfiguration`, JSON serialization attributes tied to a
  specific wire format) directly — keep those in Infrastructure/Presentation.

## Security Considerations
Authorization decisions belong in Application (use case level) or
Presentation (endpoint policy), not buried in Infrastructure — keeps the
enforcement point auditable. See `dotnet.security`.

## Testing Requirements
- Domain and Application layers are unit-testable with zero infrastructure
  (no database, no HTTP) — if a domain test needs a database, the boundary
  is wrong.
- An architecture test asserting `Domain` has no dependency on
  `Infrastructure` or any framework package.

## Common Mistakes
- Putting EF Core entity configuration attributes directly on domain
  entities, leaking persistence concerns into the domain.
- Anemic domain model: entities are plain data bags, all logic lives in
  application services — defeats the purpose of isolating business rules.
- Over-layering a CRUD service with no real invariants, adding ceremony
  with no payoff (see Anti-Patterns).

## Anti-Patterns
- **Framework-first domain**: domain classes inherit from or reference
  framework base classes.
- **God application service**: one service class handling every use case
  instead of one use case per class/handler.
- **Layering for its own sake**: applying this to a project with no
  meaningful business logic just because it's a "best practice" — see
  `rules/architecture.md` on selecting the simplest architecture that fits.

## Validation Checklist
- [ ] Domain project has no framework/infrastructure references.
- [ ] Dependency direction verified by an architecture test.
- [ ] Use cases orchestrate through ports, not concrete infrastructure types.
- [ ] API layer exposes DTOs, never domain entities.

## Definition of Done
Meets `rules/definition-of-done.md`, plus: the change compiles with the
dependency direction intact and the architecture test (if present) passes.

## Example
```csharp
// Domain — no framework references
public sealed class Order
{
    private readonly List<OrderLine> _lines = new();
    public OrderId Id { get; }
    public IReadOnlyList<OrderLine> Lines => _lines;

    public Result AddLine(ProductId productId, int quantity)
    {
        if (quantity <= 0)
            return Result.Failure("Quantity must be positive.");
        _lines.Add(new OrderLine(productId, quantity));
        return Result.Success();
    }
}

// Application — defines the port
public interface IOrderRepository
{
    Task<Order?> FindAsync(OrderId id, CancellationToken ct);
    Task SaveAsync(Order order, CancellationToken ct);
}

public sealed class AddOrderLineHandler(IOrderRepository repository)
{
    public async Task<Result> Handle(AddOrderLineCommand cmd, CancellationToken ct)
    {
        var order = await repository.FindAsync(cmd.OrderId, ct);
        if (order is null) return Result.Failure("Order not found.");

        var result = order.AddLine(cmd.ProductId, cmd.Quantity);
        if (result.IsFailure) return result;

        await repository.SaveAsync(order, ct);
        return Result.Success();
    }
}

// Infrastructure — implements the port with EF Core
public sealed class EfOrderRepository(AppDbContext db) : IOrderRepository
{
    public Task<Order?> FindAsync(OrderId id, CancellationToken ct) =>
        db.Orders.FirstOrDefaultAsync(o => o.Id == id, ct);

    public Task SaveAsync(Order order, CancellationToken ct) =>
        db.SaveChangesAsync(ct);
}
```
Trade-off: this adds a repository interface + implementation for one
aggregate — worth it because `Order` has real invariants (line quantity
validation) that must be enforced regardless of caller.

## Related Skills
- `dotnet.architecture.ddd` — where the domain modeling detail (entities,
  value objects, aggregates) this architecture protects comes from.
- `dotnet.architecture.result-rop` — the `Result` pattern used above for
  explicit failure handling instead of exceptions for expected failures.
- `dotnet.architecture.repository-specification` — repository pattern
  detail beyond the minimal example here.
