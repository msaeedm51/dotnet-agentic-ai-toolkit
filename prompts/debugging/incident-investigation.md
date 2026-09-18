---
id: prompt.debugging.incident-investigation
title: Incident Investigation
category: prompt
domain: both
related_skills: []
related_agents: [agent.devops-engineer, agent.dotnet-developer]
tags: [debugging, incident]
---

# Incident Investigation

## Purpose
Restore service safely first, understand root cause second — the direct
invocation of `workflows/production-incident.md`.

## When to Use
A live production issue currently affecting users.

## Required Context
Impact description (what's broken, for whom, how severely), and access to
logs/metrics/deployment history if available.

## Prompt

```text
Investigate this production incident: [DESCRIPTION], following
workflows/production-incident.md.

1. Assess actual impact and severity.
2. Evaluate whether an immediate mitigation exists (rollback, feature
   flag, scale-out) to stop user impact before root-causing.
3. If a mitigation is chosen, confirm impact is actually stopped/reduced
   before proceeding.
4. Investigate root cause using the same evidence-before-hypothesis
   discipline as workflows/bug-fix.md — under time pressure, not with
   less rigor.
5. Implement and test the fix.
6. Confirm the original user-facing symptom is actually resolved after
   deployment, not just that the deploy succeeded.

Communicate any deployment/rollback action before executing it.
```

## Expected Output
A stabilization decision, a confirmed root cause, a tested fix, and
confirmation the original symptom is resolved post-deployment.

## Related Skills / Agents
`agent.devops-engineer` for stabilization/deployment;
`agent.dotnet-developer` for root cause and fix; `agent.code-reviewer` for
the expedited review stage.
