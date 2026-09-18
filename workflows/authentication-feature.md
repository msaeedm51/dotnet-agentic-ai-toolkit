---
id: workflow.authentication-feature
title: Authentication Feature
category: workflow
triggers: [design authentication, add login, implement oauth, set up jwt]
agents_involved: [agent.architect, agent.security-reviewer, agent.dotnet-developer, agent.test-engineer]
skills_loaded: [dotnet.authentication, dotnet.authorization, dotnet.security]
tags: [authentication, security, multi-agent]
---

# Authentication Feature

## Purpose
Design and implement authentication/authorization with security review
built into the process from the start, not bolted on at the end — this is
the workflow example from your original spec showing
Architect → Security → Developer coordination for a security-sensitive
feature.

## When to Use
Adding or changing authentication (login, token issuance/validation,
identity provider integration) or a new authorization model.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | `agent.architect` | Requirement | AuthN/AuthZ approach | Step 3 |
| 3 | `agent.security-reviewer` | Approach | Security sign-off on design | Step 4 (if issues) or 5 |
| 4 | `agent.architect` | Security concerns | Revised approach | Step 3 (re-review) |
| 5 | `agent.dotnet-developer` | Approved design | Implementation | Step 6 |
| 6 | `agent.security-reviewer` | Implementation | Findings | Step 7 (if findings) or 8 |
| 7 | `agent.dotnet-developer` | Findings | Fixes | Step 6 (re-review) |
| 8 | `agent.test-engineer` | Implementation | Auth-boundary tests | End |

## Stages

### 1. Requirement
- **Actions:** Identify what's actually needed: new login flow, token
  validation for a resource server, a new authorization model, or an
  identity provider migration.
- **Output:** Confirmed requirement.
- **Gate:** None.

### 2. Design approach
- **Actions:** `agent.architect` proposes the approach — prefer delegating
  to a standards-based identity provider over a custom scheme
  (`dotnet.authentication`); define the authorization model (role/claims/
  resource-based, `dotnet.authorization`).
- **Output:** Proposed design.
- **Gate:** None.

### 3. Security design review
- **Actions:** `agent.security-reviewer` reviews the *design* before
  implementation starts — token validation parameters, session/refresh
  token strategy, authorization enforcement points.
- **Output:** Sign-off or concerns.
- **Gate:** No open security concern on the design before implementation
  begins — catching a design flaw here is far cheaper than after
  implementation.

### 4. Implementation
- **Actions:** `agent.dotnet-developer` implements per the approved
  design.
- **Output:** Working implementation.
- **Gate:** None beyond the standard build/compile gate.

### 5. Security implementation review
- **Actions:** `agent.security-reviewer` reviews the actual implementation
  — validates issuer/audience/signature checks are correctly wired, no
  claim is trusted before signature validation, authorization policies are
  enforced server-side.
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 6. Test authentication/authorization boundaries
- **Actions:** `agent.test-engineer` covers: valid token succeeds, expired/
  wrong-audience/tampered token → 401, every authorization policy's allow
  and deny case.
- **Output:** Passing boundary tests.
- **Gate:** Every failure mode listed above is covered by a passing test.

## Escalation
Any design uncertainty about token lifetime, refresh strategy, or
authorization model escalates to the user (`AGENTS.md` §7) rather than
picking a default — these decisions have long-lived security implications.

## Related Workflows
- `workflows/new-feature.md` — the parent workflow when auth is part of a
  larger feature.
- `workflows/code-review.md` — the general review this workflow's security
  stages specialize for auth-specific concerns.
