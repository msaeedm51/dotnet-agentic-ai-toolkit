---
id: workflow.bug-fix
title: Bug Fix (Systematic Debugging)
category: workflow
triggers: [fix this bug, debug this, something is broken, investigate this error]
agents_involved: [agent.dotnet-developer, agent.test-engineer, agent.code-reviewer]
skills_loaded: []
tags: [debugging, bug-fix]
---

# Bug Fix (Systematic Debugging)

## Purpose
Find and fix the actual root cause of a reported problem, distinguishing
observed fact from hypothesis at every step — never presenting an
unverified hypothesis as the confirmed cause.

## When to Use
Any bug report or "this isn't working" request. This is the single
debugging workflow for the toolkit — it does not have a separate
"debugging skill," since debugging is this workflow's entire purpose.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-6 | AI assistant | Symptom report | Confirmed root cause | Step 7 |
| 7 | `agent.dotnet-developer` | Root cause | Fix | Step 8 |
| 8 | `agent.test-engineer`/developer | Fix | Regression test | Step 9 |
| 9 | AI assistant | Fix + test | Validation | Step 10 |
| 10 | `agent.code-reviewer` (for non-trivial fixes) | Fix | Review | End |

## Stages

### 1. Symptom
- **Input:** The reported problem, as stated.
- **Actions:** Restate the symptom precisely — what was expected vs. what
  actually happened.
- **Output:** Precise symptom statement.
- **Gate:** None.

### 2. Reproduce
- **Actions:** Attempt to reproduce the symptom, using the available
  tools (`AGENTS.md` §2 — ask the user for steps/logs if reproduction isn't
  possible directly).
- **Output:** A reproduction, or an explicit statement that it couldn't be
  reproduced and why.
- **Gate:** None — proceed to evidence-gathering either way, but label
  confidence accordingly.

### 3. Collect evidence
- **Actions:** Gather logs, stack traces, relevant code, and any other
  observable facts. Label each as an observed fact, distinct from
  interpretation.
- **Output:** Evidence set, each item labeled as fact.
- **Gate:** None.

### 4. Form hypotheses
- **Actions:** From the evidence, form one or more hypotheses about the
  root cause — explicitly labeled as hypotheses, not facts.
- **Output:** Ranked hypothesis list.
- **Gate:** None.

### 5. Check logs / inspect code
- **Actions:** Test each hypothesis against the actual code and available
  logs/data — not just plausibility.
- **Output:** Hypotheses confirmed, refined, or eliminated.
- **Gate:** None.

### 6. Inspect database/network if required
- **Actions:** If the hypothesis involves data state or an external call,
  inspect the actual database/network behavior rather than assuming.
- **Output:** Root cause confirmed by direct evidence, or the
  investigation is explicitly stated as inconclusive.
- **Gate:** A root cause is confirmed by evidence before proceeding to a
  fix — never fix based on an unverified hypothesis alone. If genuinely
  inconclusive after reasonable investigation, say so and ask for more
  information rather than guessing at a fix.

### 7. Fix
- **Actions:** Implement the smallest change that addresses the confirmed
  root cause (`rules/general.md`) — not a broader defensive rewrite.
- **Output:** Fix.
- **Gate:** The fix directly addresses the confirmed root cause, not just
  a symptom.

### 8. Regression test
- **Actions:** Add a test that fails without the fix and passes with it —
  this proves the fix actually addresses the reported symptom
  (`rules/testing.md`).
- **Output:** Regression test.
- **Gate:** Test fails on the pre-fix code, passes on the post-fix code.

### 9. Validate
- **Actions:** Confirm the original symptom no longer reproduces; run the
  broader test suite to confirm no new regression.
- **Output:** Validation result.
- **Gate:** Original symptom resolved; no new test failures.

## Escalation
If reproduction fails after reasonable effort, or the evidence doesn't
converge on a confirmed root cause, stop and ask the user for more
information (additional logs, exact reproduction steps) rather than
shipping a speculative fix.

## Related Workflows
- `workflows/production-incident.md` — the higher-urgency variant of this
  workflow for a live production issue, with additional stakeholder/
  rollback concerns.
- `workflows/performance-investigation.md` — the performance-specific
  variant, using measurement instead of reproduction/logs as primary
  evidence.
