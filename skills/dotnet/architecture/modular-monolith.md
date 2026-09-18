---
id: dotnet.architecture.modular-monolith
title: Modular Monolith
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore]
triggers: [modular monolith, module boundaries, vertical slices, single deployable multiple modules]
requires: []
related: [dotnet.architecture.ddd, dotnet.architecture.clean-architecture, dotnet.architecture.microservices, dotnet.architecture.domain-events-outbox]
optional: []
prerequisites: [dotnet.architecture.ddd]
tags: [architecture, modularity]
---

# Modular Monolith

## Purpose
Get most of the boundary discipline of microservices (independent modules,
clear contracts, no shared mutable state) while keeping a single
deployable, single database transaction scope by default, and no network
hop between modules.

## When to Use
- Multiple bounded contexts that don't yet need independent deployment,
  scaling, or team ownership.
- A default starting point before microservices — split out a module later
  only when a concrete driver (team autonomy, independent scaling, deploy
  cadence) requires it.

## Prerequisites
`dotnet.architecture.ddd` for identifying module boundaries as bounded
contexts.

## Inputs Required
The actual bounded contexts from domain analysis — module boundaries should
match them, not an arbitrary technical split (e.g. "all controllers" vs
"all services").

## Engineering Principles
1. Each module owns its own data — no other module queries its tables
   directly, even though they're in the same database.
2. Modules communicate through explicit contracts: an internal API,
   in-process messaging, or events — never a shared entity reference across
   module boundaries.
3. A module can be extracted to its own service later with its public
   contract mostly unchanged, if the module boundary was drawn correctly.
4. Shared kernel code (cross-cutting concerns only — logging, auth
   primitives) is minimal and explicit, not a dumping ground.

## Step-by-Step Workflow
1. Identify modules from bounded contexts (see `dotnet.architecture.ddd`).
2. Give each module its own project(s): `Modules.Orders`,
   `Modules.Inventory`, etc., each internally structured per
   `dotnet.architecture.clean-architecture` if warranted.
3. Define each module's public contract (a small set of interfaces/DTOs it
   exposes) — everything else is `internal`.
4. Cross-module interaction goes through the public contract or domain/
   integration events — never a direct EF Core query into another module's
   tables.
5. Enforce boundaries with an architecture test (no project references a
   module's internal namespace from outside it).

## Code Standards
- Module internals are `internal`, not `public` — the compiler enforces
  what the contract intentionally hides.
- One `DbContext` per module (even sharing one physical database) so cross-
  module table access isn't accidentally easy.

## Architecture Constraints
No foreign key or join query spans two modules' tables directly. Cross-
module consistency is handled via events (see
`dotnet.architecture.domain-events-outbox`) or synchronous calls through the
module's public contract, with the same transactional-boundary discipline
as a microservice call.

## Security Considerations
Authorization checks live inside the module that owns the resource, not in
a shared cross-cutting filter that assumes every module has the same rules.

## Testing Requirements
An architecture test asserting no module references another module's
internal namespace. Integration tests for cross-module event flows.

## Common Mistakes
- Sharing one `DbContext` across modules "for convenience," which quietly
  reintroduces tight coupling the module structure was meant to prevent.
- Drawing module boundaries around technical layers (all APIs together, all
  services together) instead of business capability.

## Anti-Patterns
- **Distributed monolith**: modules call each other synchronously so
  extensively that they can never be deployed independently, defeating the
  purpose without the benefit of simpler ops.
- **Premature microservices**: skipping this step and going straight to
  network-separated services with no concrete driver requiring it.

## Validation Checklist
- [ ] Module boundaries match bounded contexts, not technical layers.
- [ ] No cross-module direct table access; enforced by test or DbContext
      separation.
- [ ] Public contracts are minimal and explicit; everything else `internal`.

## Definition of Done
Meets `rules/definition-of-done.md`; architecture test for module boundary
violations passes.

## Example
```csharp
// Modules.Orders — public contract, everything else internal
namespace Modules.Orders;

public interface IOrderFacade
{
    Task<Result<Guid>> PlaceOrderAsync(PlaceOrderRequest request, CancellationToken ct);
}

// Modules.Inventory reacts to an order being placed via an event,
// not by querying Modules.Orders' tables directly.
namespace Modules.Inventory;

internal sealed class OrderPlacedHandler(IInventoryRepository repo)
    : INotificationHandler<OrderPlacedEvent>
{
    public async Task Handle(OrderPlacedEvent evt, CancellationToken ct)
    {
        foreach (var line in evt.Lines)
            await repo.ReserveStockAsync(line.ProductId, line.Quantity, ct);
    }
}
```

## Related Skills
- `dotnet.architecture.ddd` — how module boundaries are identified.
- `dotnet.architecture.domain-events-outbox` — reliable cross-module event
  delivery.
- `dotnet.architecture.microservices` — the next step if a module needs
  independent deployment.
