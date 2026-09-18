---
id: workflow.production-incident
title: Production Incident
category: workflow
triggers: [production is down, incident response, outage, urgent production bug]
agents_involved: [agent.devops-engineer, agent.dotnet-developer, agent.test-engineer, agent.code-reviewer]
skills_loaded: []
tags: [incident, production]
---

# Production Incident

## Purpose
Restore service safely first, understand root cause second — the
Investigator → Developer → Test Engineer → Reviewer chain from your
original spec, adapted for the urgency and blast-radius considerations a
live incident adds on top of `workflows/bug-fix.md`.

## When to Use
A live production issue currently affecting users — distinct from a bug
report about non-production or already-mitigated behavior, which uses
`workflows/bug-fix.md` directly without the urgency-driven stages here.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | AI assistant (Investigator role) | Incident report | Impact assessment, mitigation options | Step 3 |
| 3 | `agent.devops-engineer` | Mitigation options | Stabilization action | Step 4 |
| 4-8 | Follows `workflows/bug-fix.md` stages 3-9 | Stabilized system | Confirmed root cause + fix | Step 9 |
| 9 | `agent.code-reviewer` | Fix | Expedited review | Step 10 |
| 10 | `agent.devops-engineer` | Reviewed fix | Deployed fix | End |

## Stages

### 1. Assess impact
- **Actions:** Determine what's actually broken, for whom, and how
  severely — before investigating cause, confirm whether immediate
  mitigation (rollback, feature flag, scaling) is needed to stop user
  impact.
- **Output:** Impact assessment.
- **Gate:** None.

### 2. Consider immediate mitigation
- **Actions:** If a fast, low-risk mitigation exists (rollback to the last
  known-good deployment, disabling a feature flag), evaluate it before
  committing to root-cause investigation as the path to resolution —
  restoring service and finding the root cause are not always the same
  first step.
- **Output:** Mitigation decision.
- **Gate:** A decision is made explicitly (mitigate now vs. investigate
  first) rather than defaulting to one without considering the trade-off.

### 3. Stabilize
- **Actions:** `agent.devops-engineer` executes the chosen mitigation
  (rollback, flag toggle, scale-out) if one was chosen.
- **Output:** Stabilized system (impact stopped or reduced).
- **Gate:** User impact is stopped or measurably reduced before moving to
  root-cause work, if a mitigation was available.

### 4-8. Root cause and fix
- **Actions:** Follow `workflows/bug-fix.md` stages 3-9 (collect evidence,
  form hypotheses, confirm root cause, fix, regression test) — the same
  evidence-before-hypothesis discipline applies under incident pressure,
  not less rigorously.
- **Output:** Confirmed root cause and tested fix.
- **Gate:** Same as `workflows/bug-fix.md` — root cause confirmed by
  evidence before fixing.

### 9. Expedited review
- **Actions:** `agent.code-reviewer` reviews the fix — scope narrowed to
  what's necessary for safety given urgency, but security-relevant changes
  still get `agent.security-reviewer` attention; this step is expedited,
  not skipped.
- **Output:** Review findings.
- **Gate:** No BLOCKER-severity finding remains open, even under time
  pressure.

### 10. Deploy and confirm
- **Actions:** `agent.devops-engineer` deploys the fix per the project's
  deployment process; confirm the original impact is actually resolved
  post-deployment, not just that the deploy succeeded.
- **Output:** Confirmed resolution.
- **Gate:** The original user-facing symptom is confirmed resolved.

## Escalation
Any deployment/rollback action during a live incident is communicated to
the user before executing, per this toolkit's general escalation rules
(`AGENTS.md` §7) and the host environment's own risk-confirmation
requirements for production changes — incident urgency doesn't waive that.

## Related Workflows
- `workflows/bug-fix.md` — the root-cause discipline this workflow adds
  urgency-specific stabilization stages around.
- `workflows/database-change.md` — if the fix or rollback involves a schema
  change.
