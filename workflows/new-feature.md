---
id: workflow.new-feature
title: New Feature Development
category: workflow
triggers: [add a feature, implement, build a new endpoint, new capability]
agents_involved: [agent.architect, agent.dotnet-developer, agent.test-engineer, agent.security-reviewer, agent.code-reviewer, agent.documentation-engineer]
skills_loaded: []
tags: [feature-development, multi-agent]
---

# New Feature Development

## Purpose
Take a feature requirement from "asked for" to "shipped" without skipping
straight from requirement to code — the default workflow for
`agent.dotnet-developer` on anything non-trivial.

## When to Use
A request to add new functionality to a .NET (non-agentic-AI) project. For
an agentic-AI feature, use `workflows/agentic-ai-feature.md` instead (it
follows the same shape with AI-specific stages inserted).

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | AI assistant | User request | Clarified requirement, assumptions list | Step 3 |
| 3 | `agent.architect` (if project not yet inspected) | Repository | Project Understanding | Step 4 |
| 4 | `agent.architect` | Requirement, Project Understanding | Architecture boundary decision | Step 5 |
| 5-6 | `agent.architect` | Above | Design + implementation plan | Step 7 |
| 7 | `agent.dotnet-developer` | Plan | Implementation | Step 8 |
| 8 | `agent.test-engineer` (or developer for simple cases) | Implementation | Unit + integration tests | Step 9 |
| 9 | `agent.security-reviewer` | Implementation | Security findings | Step 10 (if findings) or 11 |
| 10 | `agent.dotnet-developer` | Security findings | Fixes | Step 9 (re-review) |
| 11 | `agent.code-reviewer` | Implementation + tests | Review findings | Step 12 (if findings) or 13 |
| 12 | `agent.dotnet-developer` | Review findings | Fixes | Step 11 (re-review) |
| 13 | AI assistant | Build/test commands | Build/test results | Step 14 |
| 14 | AI assistant | All of the above | Validation against `rules/definition-of-done.md` | Step 15 |
| 15 | `agent.documentation-engineer` (if required) | Implementation | Updated docs | End |

## Stages

### 1. Requirement
- **Input:** The user's request.
- **Actions:** Restate the requirement to confirm understanding.
- **Output:** Confirmed requirement.
- **Gate:** None.

### 2. Clarify assumptions
- **Actions:** Identify gaps in the requirement; fill non-load-bearing gaps
  with a stated assumption, escalate load-bearing ones per `AGENTS.md` §7.
- **Output:** Assumptions list (if any).
- **Gate:** No unresolved load-bearing ambiguity remains.

### 3. Inspect existing code
- **Actions:** Run `workflows/project-discovery.md` if not already done
  this session; otherwise inspect the specific area the feature touches.
- **Output:** Relevant existing patterns identified.
- **Gate:** None.

### 4. Identify architecture boundary
- **Actions:** Determine which module/layer owns this feature and what
  boundaries it must respect (`rules/architecture.md`).
- **Output:** Boundary decision.
- **Gate:** None.

### 5. Design
- **Actions:** `agent.architect` proposes the approach, sized to the
  requirement (`rules/architecture.md` — simplest architecture that fits).
- **Output:** Design.
- **Gate:** Design doesn't introduce a pattern without a concrete driver.

### 6. Implementation plan
- **Actions:** Break the design into concrete steps.
- **Output:** Implementation plan.
- **Gate:** None.

### 7. Implementation
- **Actions:** `agent.dotnet-developer` implements per the plan, following
  `rules/csharp.md`, `rules/dotnet.md`, and relevant skill files.
- **Output:** Working implementation.
- **Gate:** Compiles; matches the plan.

### 8. Unit tests / Integration tests
- **Actions:** Tests added per `rules/testing.md`, covering success,
  failure, and authorization paths.
- **Output:** Passing test suite including new tests.
- **Gate:** Tests pass; every behavior change is covered.

### 9. Security review
- **Actions:** `agent.security-reviewer` checks the implementation against
  `rules/security.md`.
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 10. Code review
- **Actions:** `agent.code-reviewer` checks correctness, architecture,
  maintainability per `workflows/code-review.md`.
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 11. Build
- **Actions:** Build the project.
- **Output:** Build result.
- **Gate:** Build succeeds with no new significant warnings.

### 12. Validation
- **Actions:** Check the change against `rules/definition-of-done.md` in
  full.
- **Output:** Confirmed done, or a list of what's outstanding.
- **Gate:** All applicable Definition of Done items are satisfied.

### 13. Documentation
- **Actions:** `agent.documentation-engineer` updates docs only where
  `rules/definition-of-done.md` requires it.
- **Output:** Updated documentation (if applicable).
- **Gate:** None.

## Escalation
A gate failure at any stage returns to the responsible agent for that
stage, not forward — e.g. a security finding returns to implementation, not
to code review with the issue unresolved.

## Related Workflows
- `workflows/agentic-ai-feature.md` — the agentic-AI-track counterpart.
- `workflows/api-development.md` — API-specific detail within this
  workflow's implementation stage.
- `workflows/code-review.md` — detail for stage 10.
