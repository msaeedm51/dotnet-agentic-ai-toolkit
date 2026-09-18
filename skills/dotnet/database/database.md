---
id: dotnet.database
title: Database Design & Operations (Engine-Agnostic)
category: skill
domain: dotnet
technologies: [sql, database]
triggers: [schema design, normalization, indexing strategy, isolation levels, deadlocks, pagination, bulk operations, backup, restore]
requires: []
related: [dotnet.database.sql-server, dotnet.database.postgresql, dotnet.efcore, dotnet.performance]
optional: []
prerequisites: []
tags: [database, schema, transactions]
---

# Database Design & Operations (Engine-Agnostic)

## Purpose
Cover schema design, transaction/concurrency correctness, and operational
concerns that apply regardless of the specific engine — the engine-specific
detail lives in `dotnet.database.sql-server` / `dotnet.database.postgresql`.

## When to Use
Any schema design, migration, or query correctness/performance task. Load
the engine-specific skill alongside this one for syntax/feature detail.

## Prerequisites
None.

## Inputs Required
Which category of database this is — **application** (owned, migrated by
this codebase), **legacy** (owned elsewhere, mapped not migrated),
**read-only/reporting** (never written to by this service), or **external
data source** (accessed via an API/ETL, not direct connection). Each gets
different rules — a legacy database is never restructured to fit new code;
a reporting database is never written to from a transactional service.

## Engineering Principles
1. Normalize by default; denormalize deliberately, for a stated performance
   or query-shape reason — not preemptively.
2. Index for actual query patterns — every index has a write-cost trade-off,
   so it needs a read-pattern justification.
3. Choose the transaction isolation level for the actual consistency
   requirement — don't default to the strictest (serializable) "to be safe"
   if it causes contention the workload can't tolerate, and don't default
   to the loosest without checking what anomalies it permits.
4. Design for the deadlock possibility in any multi-statement transaction
   touching more than one table/row set — consistent access ordering
   reduces (doesn't eliminate) the risk.
5. Paginate any query that can return an unbounded result set — never
   return "all rows" to a caller by default.
6. Bulk operations (large inserts/updates/deletes) use set-based/bulk
   mechanisms, not row-by-row round trips.

## Step-by-Step Workflow
1. Classify the database (application/legacy/reporting/external) before
   proposing any schema change — this determines what's even allowed.
2. Design the schema: entities, relationships, normalization level, with
   the reason for any deliberate denormalization stated.
3. Identify indexes from actual query patterns (existing or planned), not
   speculatively for every column.
4. Choose isolation level and transaction boundaries based on the actual
   consistency requirement (see `dotnet.database.sql-server` /
   `dotnet.database.postgresql` for engine-specific isolation semantics).
5. For any query returning a list, add pagination (keyset pagination for
   large/frequently-changing datasets, offset pagination for smaller/stable
   ones).
6. For bulk operations, use the engine's bulk mechanism (bulk copy, `COPY`,
   set-based `UPDATE`/`DELETE`) instead of iterating rows in application
   code.
7. Plan migrations per `workflows/database-change.md` for downtime/locking
   impact before applying to a shared environment.

## Code Standards
Migrations are reviewed for their generated SQL, not just the model change
that produced them — an auto-generated migration can lock a large table in
a way the model diff doesn't make obvious.

## Architecture Constraints
An application database is owned by exactly one service/module
(`dotnet.architecture.modular-monolith` / `.microservices`) — no other
service queries it directly. A legacy or reporting database is read
through an explicit, narrow access layer, never treated as if this
codebase owns its schema.

## Security Considerations
Database credentials are least-privilege (the application's connection
string doesn't need `db_owner`/superuser). Backups are encrypted and access-
controlled equivalently to the live data they contain.

## Testing Requirements
Test query correctness and constraint enforcement against a real engine
instance (Testcontainers), not an abstraction that doesn't enforce the same
constraints — see `dotnet.efcore` and `dotnet.testing`.

## Common Mistakes
- Adding an index for every column "just in case," slowing down writes with
  no corresponding read benefit.
- Returning an unbounded result set from a query with no pagination, which
  works in development and times out in production.
- Treating a legacy/reporting database as safe to restructure because "it's
  just a database."

## Anti-Patterns
- **God table**: one table with dozens of nullable columns representing
  several different entity types instead of proper normalization.
- **N+1 via pagination bypass**: fetching "all rows then filtering in
  memory" instead of pushing the filter/pagination into the query.

## Validation Checklist
- [ ] Database category (application/legacy/reporting/external) identified
      before proposing a schema change.
- [ ] Every index is justified by an actual query pattern.
- [ ] Every list-returning query is paginated.
- [ ] Bulk operations use set-based mechanisms, not row-by-row loops.
- [ ] Migration reviewed for locking/downtime impact.

## Definition of Done
Meets `rules/definition-of-done.md` and `workflows/database-change.md`.

## Related Skills
- `dotnet.database.sql-server` / `dotnet.database.postgresql` —
  engine-specific syntax, execution plans, and features.
- `dotnet.efcore` — ORM-level implementation of these principles.
- `dotnet.performance` — query performance tuning.
