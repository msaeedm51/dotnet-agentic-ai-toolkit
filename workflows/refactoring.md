---
id: workflow.refactoring
title: Refactoring
category: workflow
triggers: [refactor this, clean up this code, restructure without changing behavior]
agents_involved: [agent.dotnet-developer, agent.test-engineer, agent.code-reviewer]
skills_loaded: []
tags: [refactoring]
---

# Refactoring

## Purpose
Change code structure without changing observable behavior, with a safety
net established before touching anything — refactoring without tests
covering the current behavior is just risky rewriting.

## When to Use
A request to restructure, clean up, or improve existing code with no
behavior change intended.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-4 | AI assistant | Target code | Safety net assessment | Step 5 |
| 5-6 | `agent.dotnet-developer` | Safety net | Incremental changes | Step 7 |
| 7 | AI assistant | Changes | Test results per increment | Step 5 (loop) or 8 |
| 8 | `agent.code-reviewer` | Final diff | Review | End |

## Stages

### 1. Identify current behavior
- **Actions:** Understand what the code currently does — read it, and its
  existing tests if any — before changing anything.
- **Output:** Current-behavior understanding.
- **Gate:** None.

### 2. Identify callers
- **Actions:** Find every caller/consumer of the code being refactored —
  a public API's callers may extend beyond this codebase.
- **Output:** Caller list.
- **Gate:** None.

### 3. Identify existing tests
- **Actions:** Find tests already covering this code's behavior.
- **Output:** Existing test coverage assessment.
- **Gate:** None.

### 4. Establish a safety net
- **Actions:** If existing test coverage is insufficient to catch a
  behavior change, add characterization tests for current behavior before
  refactoring — this is the safety net that makes "no behavior change"
  verifiable rather than assumed.
- **Output:** Adequate test coverage of current behavior.
- **Gate:** The refactoring target has test coverage sufficient to detect
  an accidental behavior change, before any structural change begins.

### 5. Identify risk
- **Actions:** Assess how risky the refactor is (blast radius, number of
  callers, complexity) — this determines how incremental step 6 needs to
  be.
- **Output:** Risk assessment.
- **Gate:** None.

### 6. Make incremental changes
- **Actions:** Refactor in small steps, each independently verifiable —
  not one large rewrite committed as a single unreviewable change.
- **Output:** Incremental diffs.
- **Gate:** None.

### 7. Run tests after each increment
- **Actions:** Run the safety-net tests after each incremental change.
- **Output:** Test results.
- **Gate:** Tests pass after every increment before proceeding to the
  next — a failure here means the increment broke behavior; fix or revert
  before continuing, don't push forward and hope it resolves.

### 8. Avoid unrelated changes
- **Actions:** Confirm the diff contains only structural changes — no
  behavior change, no unrelated cleanup bundled in
  (`rules/general.md`).
- **Output:** Final diff.
- **Gate:** Diff is scoped to the refactor alone.

## Escalation
If establishing an adequate safety net (step 4) would itself be a large
undertaking, say so explicitly and confirm with the user whether to proceed
with lower confidence or invest in the safety net first — don't silently
skip it.

## Related Workflows
- `workflows/new-feature.md` — when the "refactor" reveals it actually
  needs to change behavior, this is the workflow to switch to (explicitly,
  not silently).
