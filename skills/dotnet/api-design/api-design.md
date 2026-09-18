---
id: dotnet.api-design
title: API Design
category: skill
domain: dotnet
technologies: [aspnetcore, rest]
triggers: [api design, rest api, versioning, pagination, idempotency, http status codes, breaking change]
requires: []
related: [dotnet.aspnetcore, dotnet.authorization, dotnet.security]
optional: []
prerequisites: []
tags: [api, rest, contracts]
---

# API Design

## Purpose
Design an HTTP API contract that's predictable, versionable, and doesn't
break consumers unexpectedly — the "what the contract looks like" companion
to `dotnet.aspnetcore`'s "how to implement it."

## When to Use
Designing a new API surface, adding an endpoint to an existing one, or
changing an existing contract.

## Prerequisites
None.

## Inputs Required
Who the consumers are (internal service, public API, frontend only) — this
changes how strict versioning/backward-compatibility needs to be.

## Engineering Principles
1. Resources are nouns, HTTP methods carry the verb — `POST /orders`, not
   `POST /createOrder`.
2. Status codes are used per their actual HTTP semantics: 200/201/204 for
   success variants, 400 for client input errors, 401/403 for authN/authZ,
   404 for missing resources, 409 for conflicts, 422 for semantically
   invalid input, 5xx only for the server's own failure.
3. Errors return `ProblemDetails` (RFC 7807) consistently across the API.
4. DTOs are distinct from domain/persistence entities — the contract is
   designed for the consumer, not derived automatically from the database.
5. Idempotency for unsafe operations that might be retried (payments,
   order creation) via an idempotency key, not assumed from the HTTP verb
   alone.
6. Pagination, filtering, and sorting follow one consistent convention
   across the whole API, not ad hoc per endpoint.
7. A breaking change gets a new version or a documented migration path —
   never silently changes existing consumer behavior.

## Step-by-Step Workflow
1. Model the resource(s) involved and the operations as HTTP methods on
   them.
2. Define request/response DTOs, independent of internal entity shape.
3. Decide status codes for every outcome (success and each failure mode) up
   front, not reactively while implementing.
4. Decide whether the operation needs idempotency support and design the
   key mechanism if so.
5. Apply the project's existing pagination/filtering/versioning convention;
   if none exists yet, pick one and document it, don't invent a new one per
   endpoint.
6. For a breaking change to an existing endpoint, choose a versioning
   strategy (URL segment, header, media type) consistent with what the API
   already uses.

## Code Standards
DTOs are named for their purpose (`CreateOrderRequest`,
`OrderResponse`), not reused between unrelated operations just because the
shape happens to match today.

## Architecture Constraints
The contract is designed independently of the persistence model — a schema
change should not automatically become a breaking API change if the DTO
mapping absorbs it.

## Security Considerations
Response DTOs never include fields the caller isn't authorized to see —
don't rely on "the frontend just won't display it." Authorization is
enforced per resource/action, not inferred from authentication alone
(`dotnet.authorization`).

## Testing Requirements
Contract-level tests: every documented status code for an endpoint is
actually exercised by a test, including error cases.

## Common Mistakes
- Verb-shaped URLs (`/getOrder`, `/updateOrderStatus`) instead of resource-
  oriented routes with the right HTTP method.
- Returning 200 with an error payload instead of the correct 4xx/5xx status.
- Silently changing a response shape (removing/renaming a field) without
  versioning — breaks consumers with no warning.

## Anti-Patterns
- **Chatty API**: forcing the consumer into many round-trips for one logical
  operation because the resource boundary doesn't match actual use cases.
- **Kitchen-sink endpoint**: one endpoint accepting a dozen optional
  parameters that each change its behavior significantly, instead of
  distinct, well-named operations.

## Validation Checklist
- [ ] Status codes match actual HTTP semantics for every outcome.
- [ ] DTOs are distinct from persistence/domain entities.
- [ ] Breaking changes are versioned or otherwise explicitly communicated.
- [ ] Pagination/filtering/sorting follows the project's existing
      convention.

## Definition of Done
Meets `rules/definition-of-done.md`; every documented response/status code
has a test.

## Example
```csharp
public sealed record CreateOrderRequest(Guid CustomerId, IReadOnlyList<OrderLineRequest> Lines);
public sealed record OrderLineRequest(Guid ProductId, int Quantity);
public sealed record OrderResponse(Guid Id, string Status, decimal Total);

// POST /orders -> 201 Created + Location header, or 400 ProblemDetails
// GET  /orders/{id} -> 200 OK, or 404 ProblemDetails
// GET  /orders?customerId=&page=&pageSize= -> 200 OK with a consistent
//      pagination envelope used across every list endpoint in this API
```

## Related Skills
- `dotnet.aspnetcore` — implementation of this contract.
- `dotnet.authorization` — per-resource authorization detail.
- `dotnet.security` — input validation and response data exposure.
