---
id: workflow.database-change
title: Database Change
category: workflow
triggers: [schema change, add a migration, alter a table, database migration]
agents_involved: [agent.database-engineer, agent.dotnet-developer, agent.devops-engineer, agent.test-engineer]
skills_loaded: [dotnet.database, dotnet.efcore]
tags: [database, migration]
---

# Database Change

## Purpose
Take a schema change from requirement to deployed with backward
compatibility, data migration, and rollback explicitly planned — never
just "add the migration and apply it."

## When to Use
Any change to a database schema: new table/column, altered constraint,
index change, or data migration.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | `agent.database-engineer` | Requirement | Schema impact assessment | Step 3 |
| 3-4 | `agent.database-engineer` | Assessment | Migration strategy | Step 5 |
| 5 | `agent.dotnet-developer` | Migration strategy | Application code changes | Step 6 |
| 6 | `agent.test-engineer` | Migration + code | Tests | Step 7 |
| 7 | `agent.devops-engineer` | Migration | Deployment/rollback plan | End |

## Stages

### 1. Requirement → schema impact
- **Actions:** Determine what schema change is actually needed, and
  classify the database (application/legacy/reporting/external —
  `dotnet.database`).
- **Output:** Schema impact assessment.
- **Gate:** Database classification confirmed before proceeding.

### 2. Backward compatibility
- **Actions:** Determine whether the change is backward-compatible with
  the currently-deployed application version (matters for zero-downtime
  deploys where old and new code may run simultaneously during rollout).
- **Output:** Compatibility assessment.
- **Gate:** An incompatible change has an explicit multi-step migration
  plan (expand-migrate-contract), not a single breaking step.

### 3. Migration strategy
- **Actions:** Design the migration: additive first (new nullable column/
  new table), backfill if needed, then any destructive step (dropping an
  old column) as a separate, later migration after the application no
  longer depends on it.
- **Output:** Migration strategy, sequenced.
- **Gate:** No single migration both adds a new requirement and removes
  the old path in one step, for a zero/minimal-downtime requirement.

### 4. Data migration
- **Actions:** For a change requiring data backfill, plan it as a bounded,
  resumable operation (batched, not a single unbounded update) —
  `dotnet.database` bulk operation guidance.
- **Output:** Data migration plan.
- **Gate:** Backfill is batched/bounded if the affected table is large.

### 5. Application changes
- **Actions:** Update application code (EF Core model, queries) to match
  the new schema.
- **Output:** Application code changes.
- **Gate:** Application code and migration are consistent.

### 6. Testing
- **Actions:** Integration-test the migration and the application code
  against a real database engine (Testcontainers) — `dotnet.testing`.
- **Output:** Passing tests.
- **Gate:** Migration applies cleanly to a copy of representative data;
  application code works against the post-migration schema.

### 7. Rollback strategy
- **Actions:** Define the rollback path — a down-migration where feasible,
  or a forward-fix plan if a clean rollback isn't possible (common for
  destructive changes) — and any downtime/locking risk for the target
  environment.
- **Output:** Rollback/deployment plan.
- **Gate:** A rollback or forward-fix plan exists before applying to a
  shared/production environment.

### 8. Deployment
- **Actions:** Apply the migration per the sequenced plan, coordinated
  with the corresponding application deployment.
- **Output:** Deployed change.
- **Gate:** Health checks pass post-deployment; no unexpected locking/
  downtime observed.

## Escalation
A migration expected to lock a large table or require significant downtime
escalates to `agent.architect`/the user for a scheduling decision before
being applied to a shared environment.

## Related Workflows
- `workflows/new-feature.md` — the parent workflow when a database change
  is part of a larger feature.
- `workflows/production-incident.md` — if a migration causes a production
  issue, that workflow governs the response.
