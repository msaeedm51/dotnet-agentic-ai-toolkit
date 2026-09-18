---
id: workflow.api-development
title: API Development
category: workflow
triggers: [design and build an endpoint, add an api, expose a new resource]
agents_involved: [agent.api-engineer, agent.security-reviewer, agent.test-engineer]
skills_loaded: [dotnet.api-design, dotnet.aspnetcore]
tags: [api, rest]
---

# API Development

## Purpose
Design and implement an HTTP endpoint with the contract decided
deliberately up front — status codes, DTOs, authorization, versioning —
rather than reactively while writing the handler.

## When to Use
Adding a new endpoint or resource to an existing API, or designing a new
API surface. Runs as a specialization of `workflows/new-feature.md`'s
implementation stage when the feature is API-shaped.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | `agent.api-engineer` | Requirement | Resource/contract design | Step 3 |
| 3-4 | `agent.api-engineer` | Contract design | DTOs + implementation | Step 5 |
| 5 | `agent.security-reviewer` | Implementation | Authorization/input validation findings | Step 6 or 4 (if findings) |
| 6 | `agent.test-engineer` | Implementation | API tests | End |

## Stages

### 1. Model the resource
- **Actions:** Identify the resource(s) and operations as HTTP methods on
  them (`dotnet.api-design`) — not verb-shaped URLs.
- **Output:** Resource model.
- **Gate:** None.

### 2. Decide the contract
- **Actions:** Decide status codes for every outcome, DTO shapes,
  pagination/filtering/versioning approach consistent with the existing
  API, and idempotency needs.
- **Output:** Contract decision.
- **Gate:** Contract is consistent with the rest of the API's existing
  conventions, or a deviation is explicitly justified.

### 3. Define DTOs
- **Actions:** Define request/response types distinct from domain/
  persistence entities.
- **Output:** DTOs.
- **Gate:** No domain entity is used as a request/response type.

### 4. Implement
- **Actions:** Implement the endpoint per `dotnet.aspnetcore`, delegating
  business logic to the application layer; apply an explicit authorization
  policy.
- **Output:** Working endpoint.
- **Gate:** Input is validated at the boundary; authorization policy is
  explicit and not left at an implicit default.

### 5. Security review
- **Actions:** `agent.security-reviewer` checks authorization enforcement,
  input validation, and data exposure in the response shape.
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 6. API tests
- **Actions:** `agent.test-engineer` adds `WebApplicationFactory`-based
  tests covering success, validation failure, and authorization failure.
- **Output:** Passing API test suite.
- **Gate:** Every documented status code for this endpoint has a test.

## Escalation
A breaking change to an existing contract escalates to `agent.architect`
for a versioning decision before implementation proceeds
(`rules/api.md` — document breaking changes).

## Related Workflows
- `workflows/new-feature.md` — the parent workflow this specializes.
- `workflows/authentication-feature.md` — when the endpoint's own auth
  mechanism is being built, not just consumed.
