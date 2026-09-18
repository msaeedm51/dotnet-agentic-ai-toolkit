---
id: rule.database
title: Database Rules
category: rule
tech_tags: [sql, efcore, sqlserver, postgresql]
triggers: [database rules, migration rule, index rule, query rule]
severity: blocking
tags: [database]
---

# Database Rules

## Classify the database before changing it

**Rule:** Before proposing a schema change, confirm whether the database is
application-owned, legacy, read-only/reporting, or an external source
(`dotnet.database`). A legacy or reporting database is never restructured
to fit new application code.

**Why:** Treating a database this codebase doesn't own as if it does risks
breaking other consumers with no visibility into them.

**Applies to:** Every schema/migration change.

**Exception:** None — this check always happens first.

---

## Every index is justified by an actual query pattern

**Rule:** A new index exists because a specific, real query needs it —
stated explicitly — not added speculatively "in case it helps."

**Why:** Every index has a write-cost trade-off; an unjustified index is
pure cost with no corresponding benefit.

**Applies to:** Every new index.

**Exception:** None.

---

## Every list-returning query is paginated

**Rule:** A query that can return an unbounded number of rows is paginated
— never "return everything" with an implicit assumption the result set
stays small.

**Why:** An unbounded query works fine in development and becomes a timeout
or memory problem in production as data grows.

**Applies to:** Every list-returning query/endpoint.

**Exception:** A query provably bounded by a small, fixed cardinality (e.g.
a lookup table with a known small row count).

---

## Migrations are reviewed for locking/downtime impact

**Rule:** A migration's generated SQL is reviewed for its actual impact on
a large or heavily-used table (a long lock, a full table rewrite) before
applying it to a shared environment — see `workflows/database-change.md`.

**Why:** An auto-generated migration can lock a large table for minutes
without the model-level diff making that obvious.

**Applies to:** Every migration applied to a shared/production database.

**Exception:** A greenfield database with no production traffic yet.

---

## Raw SQL is always parameterized

**Rule:** Raw SQL, wherever used, is parameterized (`FromSqlInterpolated`
or explicit parameters) — never string-concatenated with input, including
"trusted" internal input.

**Why:** String-concatenated SQL is a direct SQL injection vector; "it's
internal input" is not a reliable safety boundary over time as code
changes.

**Applies to:** Every raw SQL statement.

**Exception:** None.

---

## Read-only queries do not track entities

**Rule:** A query whose result won't be modified and saved back uses
`AsNoTracking()` (or the equivalent for the ORM in use).

**Why:** Tracking has real overhead and is easy to forget to disable,
degrading performance at scale for no benefit.

**Applies to:** Every read-only EF Core query.

**Exception:** None.

---

## Bulk operations use set-based mechanisms

**Rule:** An operation touching many rows uses a bulk/set-based mechanism
(`ExecuteUpdateAsync`/`ExecuteDeleteAsync`, `SqlBulkCopy`, `COPY`) — not a
loop issuing one round trip per row.

**Why:** Row-by-row operations at any real scale are orders of magnitude
slower than the engine's native bulk mechanisms.

**Applies to:** Any operation affecting more than a handful of rows.

**Exception:** A genuinely small, bounded row count where the difference is
immaterial.
