---
id: prompt.database.database-optimization
title: Database Query Optimization
category: prompt
domain: dotnet
related_skills: [dotnet.database, dotnet.database.sql-server, dotnet.database.postgresql]
related_agents: [agent.database-engineer]
tags: [database, performance]
---

# Database Query Optimization

## Purpose
Optimize a slow query with evidence (an execution plan), not a guess at
what might help.

## When to Use
A specific slow query has been identified and needs investigation.

## Required Context
The query, the engine (SQL Server or PostgreSQL —
`.ai/config.yaml`), and, ideally, an execution plan or `EXPLAIN ANALYZE`
output.

## Prompt

```text
Optimize this query: [QUERY], following dotnet.database and the
engine-specific skill (dotnet.database.sql-server or .postgresql).

1. Get the actual execution plan (or ask for it if unavailable) — do not
   guess at the bottleneck.
2. Identify the specific cause: missing/non-covering index, non-SARGable
   predicate, N+1 pattern, wrong isolation level causing contention, or
   something else the plan reveals.
3. Propose a targeted fix (index, query rewrite, projection change).
4. State the trade-off of any new index (write cost) or isolation-level
   change.
5. If possible, show the expected plan change; if not, state that the
   improvement is unverified in this environment.
```

## Expected Output
A root-caused diagnosis backed by the execution plan, a targeted fix, and
an honest statement of whether the improvement was actually measured.

## Related Skills / Agents
`agent.database-engineer` executes; escalate to
`agent.performance-engineer` if the issue turns out to be application-side
(N+1 from a loop, not the query itself).
