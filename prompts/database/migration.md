---
id: prompt.database.migration
title: Database Migration Planning
category: prompt
domain: dotnet
related_skills: [dotnet.database, dotnet.efcore]
related_agents: [agent.database-engineer]
tags: [database, migration]
---

# Database Migration Planning

## Purpose
Plan a schema change with backward compatibility, downtime, and rollback
considered explicitly — the direct invocation of
`workflows/database-change.md`.

## When to Use
Any schema change: new table/column, altered constraint, index change, or
data backfill.

## Required Context
The desired schema change, the database classification
(application/legacy/reporting/external — `dotnet.database`), and whether
zero-downtime deployment is required.

## Prompt

```text
Plan the migration for: [SCHEMA CHANGE], following
workflows/database-change.md.

1. Confirm the database classification before proceeding.
2. Assess backward compatibility with the currently-deployed application
   version.
3. Sequence the migration: additive steps first, destructive steps (if
   any) as a separate, later migration after the application no longer
   depends on the old shape.
4. Plan any data backfill as a bounded, batched operation if the table is
   large.
5. Define the rollback or forward-fix path.
6. Flag any locking/downtime risk for the target environment.

Do not combine an additive and a destructive change in the same migration
if zero/minimal downtime is required.
```

## Expected Output
A sequenced migration plan (possibly multiple migrations), a backfill plan
if needed, and an explicit rollback strategy — ready to implement per
`workflows/database-change.md`.

## Related Skills / Agents
`agent.database-engineer` executes; `agent.devops-engineer` for the
deployment coordination stage.
