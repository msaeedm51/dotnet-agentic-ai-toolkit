---
id: dotnet.database.sql-server
title: SQL Server
category: skill
domain: dotnet
technologies: [sqlserver, efcore]
triggers: [sql server, mssql, execution plan, clustered index, tsql, deadlock, isolation level sql server]
requires: [dotnet.database]
related: [dotnet.efcore, dotnet.performance]
optional: []
prerequisites: [dotnet.database]
tags: [database, sqlserver]
---

# SQL Server

## Purpose
Engine-specific detail for SQL Server: indexing (clustered vs. nonclustered),
execution plans, isolation levels, and locking/deadlock behavior — applying
the general principles in `dotnet.database` with SQL Server's actual
mechanisms.

## When to Use
Any schema, query, or performance work where the project's database is SQL
Server (`.ai/config.yaml` → `backend.database: sqlserver`).

## Prerequisites
`dotnet.database`.

## Inputs Required
Whether the query/schema concern is about correctness (locking,
transactions) or performance (indexing, execution plan).

## Engineering Principles
1. Every table has a clustered index (usually the primary key) — it defines
   physical row order; choose it deliberately, not just "identity column by
   default" if the access pattern says otherwise (e.g. a naturally
   sequential key avoids page-split fragmentation better than a random
   GUID).
2. Nonclustered indexes are added for actual `WHERE`/`JOIN`/`ORDER BY`
   patterns; include covering columns to avoid key lookups when a query is
   hot enough to matter.
3. Default isolation level is READ COMMITTED; consider READ COMMITTED
   SNAPSHOT (RCSI) to reduce reader/writer blocking if the workload suffers
   from it — understand the tempdb cost before enabling it.
4. Deadlocks are resolved by consistent access ordering across
   transactions that touch multiple tables/rows, and by keeping
   transactions short.
5. Read actual execution plans (not just guesses) before and after an
   index/query change — a plan showing a table scan where a seek was
   expected is the concrete signal something's wrong.

## Step-by-Step Workflow
1. For a new/changed query, capture the actual execution plan (SSMS,
   `SET STATISTICS IO/TIME ON`, or Azure Data Studio) rather than
   guessing at performance.
2. If the plan shows a scan where a seek is expected, check for a missing
   or non-covering index, or a non-SARGable predicate (e.g. a function
   applied to the indexed column in the `WHERE` clause).
3. For a new table, choose the clustered index deliberately based on the
   dominant access pattern.
4. For contention/blocking issues, check the actual isolation level and
   transaction duration before assuming an index will fix it — many
   blocking issues are transaction-scope, not indexing, problems.
5. For bulk load, use `SqlBulkCopy` or minimally-logged bulk insert
   patterns instead of row-by-row `INSERT`.

## Code Standards
Migrations that add a nonclustered index to a large existing table are
reviewed for online-index-creation options (`ONLINE = ON`, Enterprise/Azure
SQL) to avoid a long blocking operation on a shared environment.

## Architecture Constraints
See `dotnet.database` — applies unchanged.

## Security Considerations
Use a least-privilege application login (not `sa`/`db_owner`); enable
Transparent Data Encryption or Always Encrypted for sensitive columns where
required; audit access to sensitive tables if compliance requires it.

## Testing Requirements
Integration tests against a real SQL Server instance (Testcontainers'
`mssql` module), not the EF Core in-memory provider, for anything relying
on SQL Server-specific behavior (isolation semantics, computed columns,
`MERGE`).

## Common Mistakes
- Assuming a GUID primary key is fine as the clustered index without
  considering page-split fragmentation under high insert volume — consider
  a sequential key (`NEWSEQUENTIALID()` or an application-generated
  sequential GUID) if this matters at the project's scale.
- Wrapping a long-running operation in a transaction that holds locks far
  longer than necessary, causing blocking for unrelated requests.
- Adding an index without checking the execution plan actually uses it.

## Anti-Patterns
- **Index everything**: adding a nonclustered index per column instead of
  per actual query pattern, bloating write cost.
- **SERIALIZABLE by default**: using the strictest isolation level
  everywhere "to be safe," causing unnecessary blocking under load.

## Validation Checklist
- [ ] Clustered index chosen deliberately for the table's access pattern.
- [ ] New indexes verified against an execution plan, not assumed.
- [ ] Isolation level matches the actual consistency requirement.
- [ ] Bulk operations use `SqlBulkCopy`/set-based SQL, not row-by-row loops.

## Definition of Done
Meets `rules/definition-of-done.md` and `dotnet.database`'s checklist;
execution plan reviewed for any query targeted at a performance fix.

## Example
```sql
-- Covering index avoiding a key lookup for a hot query filtering + selecting
-- a small column set
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId_Status
    ON Orders (CustomerId, Status)
    INCLUDE (SubmittedAtUtc, Total);

-- Reduce reader/writer blocking for a read-heavy, contention-prone workload
ALTER DATABASE CURRENT SET READ_COMMITTED_SNAPSHOT ON;
```

## Related Skills
- `dotnet.database` — engine-agnostic principles this specializes.
- `dotnet.efcore` — ORM-level query generation targeting SQL Server.
- `dotnet.performance` — broader performance investigation process.
