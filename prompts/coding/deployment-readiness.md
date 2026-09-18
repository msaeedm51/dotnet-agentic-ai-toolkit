---
id: prompt.coding.deployment-readiness
title: Deployment Readiness
category: prompt
domain: dotnet
related_skills: [dotnet.docker, dotnet.azure, dotnet.linux]
related_agents: [agent.devops-engineer]
tags: [deployment, devops]
---

# Deployment Readiness

## Purpose
Check a change's deployment implications explicitly — configuration,
migrations, rollback, health checks — before it ships.

## When to Use
Before deploying a change with any deployment-relevant surface: new
configuration, a schema change, a new external dependency, or a new
service/container.

## Required Context
The change being deployed, and the target platform
(`.ai/config.yaml` → `deployment.platform`).

## Prompt

```
Assess deployment readiness for: [CHANGE].

1. Identify every new/changed configuration value and confirm it's set
   correctly (and secrets are in the secret store, not committed) for the
   target environment.
2. Identify any database migration involved and confirm
   workflows/database-change.md's rollback/downtime plan exists.
3. Confirm health checks (liveness/readiness) reflect the change's actual
   dependencies.
4. Confirm the deployment pipeline runs tests and gates deploy on them
   passing.
5. State the rollback plan for this specific change.
6. Identify any breaking change to a contract other services depend on.

Flag anything missing rather than assuming it's handled elsewhere.
```

## Expected Output
A go/no-go readiness assessment with any gap named explicitly, not a
generic checklist marked complete without verification.

## Related Skills / Agents
`agent.devops-engineer` executes; `agent.database-engineer` for
migration-specific detail.
