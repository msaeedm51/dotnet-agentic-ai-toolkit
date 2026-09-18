---
id: rule.api
title: API Rules
category: rule
tech_tags: [aspnetcore, rest]
triggers: [api rules, status code rules, dto rule, breaking change rule]
severity: blocking
tags: [api]
---

# API Rules

## Validate input at boundaries

**Rule:** Every value entering the API from a request is validated before
reaching application/domain logic — type, range, and format.

**Why:** Unvalidated input reaching domain logic either causes a confusing
downstream failure or, worse, silently corrupts state.

**Applies to:** Every endpoint accepting input.

**Exception:** None.

---

## Use consistent HTTP semantics

**Rule:** Status codes match their actual HTTP meaning consistently across
the whole API (`dotnet.api-design`) — 400 for client input errors, 401/403
for authN/authZ, 404 for missing resources, 409 for conflicts, 5xx only for
server failure.

**Why:** Inconsistent status code usage forces every consumer to special-
case this API instead of relying on standard HTTP semantics.

**Applies to:** Every endpoint.

**Exception:** None.

---

## Do not expose domain entities directly

**Rule:** Endpoints accept and return DTOs, never the tracked domain/
persistence entity.

**Why:** Exposing entities directly couples the wire contract to the
internal model and can leak fields (or ORM tracking behavior) the consumer
was never meant to see.

**Applies to:** Every endpoint.

**Exception:** None.

---

## Use DTOs/contracts

**Rule:** Request/response shapes are explicit, named types
(`CreateOrderRequest`, `OrderResponse`), not anonymous types or the domain
entity reused across unrelated operations.

**Why:** A named, explicit contract is what makes the API self-documenting
and lets a shape change be reviewed as the contract change it is.

**Applies to:** Every endpoint.

**Exception:** None.

---

## Return predictable error responses

**Rule:** Errors return `ProblemDetails` (RFC 7807) consistently across the
API — never a bespoke error shape per endpoint, and never a 200 status with
an error payload in the body.

**Why:** A consumer needs one error-handling code path, not one per
endpoint's idiosyncratic error format.

**Applies to:** Every endpoint's error responses.

**Exception:** None.

---

## Document breaking changes

**Rule:** A change to an existing endpoint's request/response shape,
status codes, or behavior that would break an existing consumer is
versioned or otherwise explicitly communicated — never shipped silently.

**Why:** A silent breaking change fails for every consumer at once, usually
discovered by them, not by the team that shipped it.

**Applies to:** Any change to a published API contract.

**Exception:** The endpoint has no external consumers yet (pre-release,
internal-only with no other team depending on it) — verify this, don't
assume it.

---

## Enforce authorization at the appropriate boundary

**Rule:** Every non-public endpoint has an explicit authorization policy
enforced server-side — never inferred from the client UI or assumed from
authentication alone.

**Why:** Authentication proves identity, not permission; skipping explicit
authorization is a direct path to a privilege-escalation vulnerability.

**Applies to:** Every non-public endpoint.

**Exception:** None.
