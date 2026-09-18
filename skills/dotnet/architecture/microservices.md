---
id: dotnet.architecture.microservices
title: Microservices
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore, docker]
triggers: [microservices, independent services, service per team, distributed system]
requires: []
related: [dotnet.architecture.modular-monolith, dotnet.architecture.event-driven, dotnet.messaging, dotnet.docker]
optional: []
prerequisites: [dotnet.architecture.modular-monolith]
tags: [architecture, distributed-systems]
---

# Microservices

## Purpose
Enable independent deployment, scaling, and team ownership of a service
boundary, at the cost of network calls, eventual consistency, and
significantly more operational complexity than a modular monolith.

## When to Use
- A concrete driver exists: independent scaling needs, independent deploy
  cadence, team autonomy across a real organizational boundary.
- Not as a default starting architecture — start with
  `dotnet.architecture.modular-monolith` and extract a service only when a
  module's boundary is proven and a driver justifies the extraction cost.

## Prerequisites
A modular monolith (or equivalent) with a module boundary already drawn
cleanly enough to extract.

## Inputs Required
The specific driver forcing the split (stated explicitly, not assumed) and
the consistency requirements across the new service boundary.

## Engineering Principles
1. Each service owns its data exclusively — no other service reads its
   database directly.
2. Cross-service communication is either synchronous (HTTP/gRPC, with
   resilience — timeouts, retries, circuit breaking) or asynchronous
   (messaging/events) — choose deliberately per interaction, not by default.
3. Consistency across services is eventual; design for it explicitly (sagas,
   outbox, compensating actions) rather than assuming a distributed
   transaction.
4. Each service is independently deployable and versioned; a breaking
   contract change needs a compatibility strategy, not a coordinated
   simultaneous deploy.

## Step-by-Step Workflow
1. Confirm the driver for extraction is real and the module boundary is
   already clean (few/no direct dependencies on other modules' internals).
2. Define the service's public API contract (HTTP/gRPC) and/or events it
   publishes/consumes.
3. Give it its own datastore; migrate data ownership, not just code.
4. Add resilience to every cross-service call: timeout, retry with backoff,
   circuit breaker (`dotnet.dotnet` — `HttpClientFactory` + resilience).
5. Add observability: distributed tracing correlation across the new
   network boundary (`dotnet.dotnet` — OpenTelemetry).
6. Plan deployment/versioning strategy for contract changes before the
   first breaking change happens.

## Code Standards
Service boundaries are HTTP/gRPC contracts or message schemas — never a
shared library exposing internal domain types across services (that
recreates tight coupling over the network).

## Architecture Constraints
No service queries another service's database. No shared mutable state
between services beyond what's explicitly published through a contract.

## Security Considerations
Service-to-service auth (mTLS or token-based), least-privilege network
policies, and no service trusting another's input without validation —
treat inter-service calls with the same rigor as external API input.

## Testing Requirements
Contract tests between services (consumer-driven or schema-based) in
addition to each service's own unit/integration tests — catching a breaking
contract change is more valuable here than end-to-end tests across the
whole system.

## Common Mistakes
- Extracting a service before the module boundary was actually clean,
  resulting in chatty, tightly coupled cross-service calls.
- No compatibility strategy for contract changes, causing coordinated
  "deploy both at once" releases that defeat independent deployability.

## Anti-Patterns
- **Distributed monolith**: services that must be deployed together to work
  correctly — all the network cost, none of the independence benefit.
- **Shared database microservices**: multiple services reading/writing the
  same tables — this is a modular monolith with extra network latency, not
  a microservice architecture.

## Validation Checklist
- [ ] Service owns its data exclusively.
- [ ] Every cross-service call has a timeout and a defined failure behavior.
- [ ] A breaking contract change has a versioning/compatibility plan.
- [ ] Distributed tracing correlates a request across service boundaries.

## Definition of Done
Meets `rules/definition-of-done.md`; contract tests exist for the new/
changed service boundary; resilience policies are in place for new
outbound calls.

## Example
```csharp
builder.Services.AddHttpClient<IInventoryClient, InventoryClient>(c =>
    {
        c.BaseAddress = new Uri(config["Services:Inventory:BaseUrl"]!);
        c.Timeout = TimeSpan.FromSeconds(5);
    })
    .AddStandardResilienceHandler(); // retry + circuit breaker + timeout
```
Trade-off: adds a network dependency with its own failure mode — the
calling service must define what happens when Inventory is unavailable
(fail the request, degrade gracefully, or queue for later) rather than
assuming it's always reachable.

## Related Skills
- `dotnet.architecture.modular-monolith` — the usual starting point before
  extraction.
- `dotnet.architecture.event-driven` — async alternative to synchronous
  service calls.
- `dotnet.messaging` — messaging infrastructure for async communication.
