---
id: workflow.code-review
title: Code Review
category: workflow
triggers: [review this pr, review my code, code review]
agents_involved: [agent.code-reviewer, agent.security-reviewer, agent.performance-engineer]
skills_loaded: []
tags: [review]
---

# Code Review

## Purpose
Produce structured, actionable findings on a diff/PR — covering
correctness, architecture, security, performance, maintainability, testing,
observability, compatibility, and deployment — without generating an
arbitrary numeric score.

## When to Use
Any request to review a diff/PR, and as the review stage embedded in
`workflows/new-feature.md`, `.bug-fix.md`, and others.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | `agent.code-reviewer` | Diff/PR | Correctness/architecture/maintainability findings | Step 5 |
| 3 | `agent.security-reviewer` (for security-relevant diffs) | Diff | Security findings | Step 5 |
| 4 | `agent.performance-engineer` (for performance-relevant diffs) | Diff | Performance findings | Step 5 |
| 5 | `agent.code-reviewer` | All findings | Consolidated, severity-ranked report | End |

## Stages

### 1. Scope the review
- **Actions:** Identify what changed and what domains it touches (data
  access, auth, API contract, agentic-AI behavior) to determine which
  specialist reviewers (security, performance) need to weigh in.
- **Output:** Review scope.
- **Gate:** None.

### 2. Correctness, architecture, maintainability review
- **Actions:** `agent.code-reviewer` checks: does the code do what it
  claims including edge/failure cases; does it respect
  `rules/architecture.md`; is it maintainable (naming, complexity, dead
  code); are breaking changes identified.
- **Output:** Findings.
- **Gate:** None — findings feed into consolidation.

### 3. Security review (when scoped in)
- **Actions:** `agent.security-reviewer` checks authN/authZ, secrets,
  injection classes, sensitive data exposure per `rules/security.md`
  (and `rules/agentic-ai.md` for agentic-AI diffs).
- **Output:** Security findings.
- **Gate:** None — findings feed into consolidation.

### 4. Performance review (when scoped in)
- **Actions:** `agent.performance-engineer` checks for N+1, allocation
  hot spots, missing resilience on new I/O — flagged as findings only when
  there's a real, evidenced concern, not speculative.
- **Output:** Performance findings.
- **Gate:** None — findings feed into consolidation.

### 5. Consolidate and report
- **Actions:** Merge all findings into one report. Each finding states:
  severity (BLOCKER/HIGH/MEDIUM/LOW/INFO), location, problem, impact,
  recommendation. No duplicate findings for the same root cause. No
  arbitrary aggregate score.
- **Output:** Final review report.
- **Gate:** Every finding has a concrete location and failure scenario, not
  a vague concern.

## Severity Definitions
- **BLOCKER** — must be fixed before merge (correctness bug, security
  vulnerability, broken build/tests).
- **HIGH** — should be fixed before merge; significant risk if shipped.
- **MEDIUM** — should be addressed soon; not blocking.
- **LOW** — minor improvement, non-blocking.
- **INFO** — observation, no action required.

## Escalation
A BLOCKER-severity security finding blocks merge regardless of other
reviewers' sign-off (`agent.security-reviewer`'s constraint in
`agents/security-reviewer.md`).

## Related Workflows
- `workflows/new-feature.md`, `.bug-fix.md`, `.refactoring.md`,
  `.database-change.md`, `.agentic-ai-feature.md` — all embed this
  workflow as their review stage.
