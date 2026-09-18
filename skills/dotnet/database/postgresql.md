---
id: dotnet.database.postgresql
title: PostgreSQL
category: skill
domain: dotnet
technologies: [postgresql, efcore]
triggers: [postgresql, postgres, pgvector, explain analyze, mvcc, vacuum, postgres isolation level]
requires: [dotnet.database]
related: [dotnet.efcore, dotnet.performance, agentic-ai.vector-search]
optional: []
prerequisites: [dotnet.database]
tags: [database, postgresql]
---

# PostgreSQL

## Purpose
Engine-specific detail for PostgreSQL: MVCC/vacuum behavior, indexing
(including `pgvector` for embeddings), execution plans, and isolation
levels — applying the general principles in `dotnet.database` with
PostgreSQL's actual mechanisms.

## When to Use
Any schema, query, or performance work where the project's database is
PostgreSQL (`.ai/config.yaml` → `backend.database: postgresql`), including
when it's used as a vector store for a RAG feature via `pgvector`.

## Prerequisites
`dotnet.database`.

## Inputs Required
Whether the concern is correctness (MVCC visibility, isolation), performance
(indexing, `EXPLAIN ANALYZE`), or vector search (`pgvector`).

## Engineering Principles
1. PostgreSQL uses MVCC — writers don't block readers by default; understand
   this before reaching for a stricter isolation level "to prevent
   blocking" that Postgres often doesn't have in the first place.
2. Dead tuples from updates/deletes need `VACUUM` (autovacuum by default) —
   a table with heavy update/delete churn and misconfigured autovacuum
   bloats and slows down; this is an operational concern to monitor, not
   just a schema one.
3. Default isolation is READ COMMITTED; use REPEATABLE READ or SERIALIZABLE
   only for a specific concurrency anomaly you've identified, and understand
   Postgres will raise a serialization failure you must retry rather than
   silently block.
4. B-tree indexes for equality/range queries; GIN/GiST for full-text,
   JSONB, or array containment queries; specialized index types
   (`ivfflat`/`hnsw` via `pgvector`) for vector similarity search.
5. Use `EXPLAIN (ANALYZE, BUFFERS)` to see actual execution, not just the
   planner's estimate.

## Step-by-Step Workflow
1. For a new/changed query, run `EXPLAIN (ANALYZE, BUFFERS)` to see the
   actual plan and buffer usage, not just estimated cost.
2. Choose index type by query shape: B-tree for equality/range, GIN for
   JSONB/array/full-text containment, `pgvector`'s `ivfflat`/`hnsw` for
   nearest-neighbor vector search (see `agentic-ai.vector-search` for the
   RAG-specific usage).
3. For high-churn tables, verify autovacuum settings are tuned for the
   table's actual update/delete rate rather than left at global defaults.
4. For contention, check whether MVCC already avoids the blocking you're
   worried about before adding a stricter isolation level.
5. For bulk load, use `COPY` instead of row-by-row `INSERT`.

## Code Standards
Migrations enabling an extension (`pgvector`, `pg_trgm`) are explicit and
reviewed — an extension changes what's available cluster-wide, not just in
this schema.

## Architecture Constraints
See `dotnet.database` — applies unchanged. A `pgvector` column used for RAG
retrieval is still owned by the service/module that owns the surrounding
data — don't let a "shared vector database" become an implicit cross-module
integration point.

## Security Considerations
Use a least-privilege role for the application connection (not the
superuser). Enable `pgcrypto`/column-level encryption or row-level security
where compliance requires it. Never construct a raw SQL string with
interpolated user input, even for dynamic filtering — use parameters.

## Testing Requirements
Integration tests against a real PostgreSQL instance (Testcontainers'
`postgres` module), not the EF Core in-memory provider, for anything
relying on Postgres-specific behavior (JSONB queries, `pgvector` similarity
search, `ON CONFLICT` upserts).

## Common Mistakes
- Reaching for SERIALIZABLE isolation to fix a blocking problem that MVCC
  already doesn't have — the actual issue is usually elsewhere (long
  transactions, missing index).
- Ignoring autovacuum tuning on a high-churn table, leading to bloat and
  slow sequential scans over time.
- Using a B-tree index for a `pgvector` similarity search column — needs
  `ivfflat`/`hnsw`, not a default index type.

## Anti-Patterns
- **Unbounded vector scan**: running a similarity search over an
  un-indexed `pgvector` column at any real scale — always index for the
  intended distance metric.
- **JSONB as a schema dodge**: storing structured, queryable data as JSONB
  to avoid a schema migration, then querying it with slow, unindexed JSONB
  path expressions.

## Validation Checklist
- [ ] Execution plan (`EXPLAIN ANALYZE`) reviewed for a targeted query
      change.
- [ ] Index type matches the query shape (B-tree/GIN/`ivfflat`/`hnsw`).
- [ ] Autovacuum considered for high-churn tables.
- [ ] Bulk operations use `COPY`, not row-by-row inserts.

## Definition of Done
Meets `rules/definition-of-done.md` and `dotnet.database`'s checklist;
execution plan reviewed for any query targeted at a performance fix.

## Example
```sql
-- pgvector similarity search index for RAG retrieval (see agentic-ai.vector-search)
CREATE INDEX ON document_chunks
    USING hnsw (embedding vector_cosine_ops);

-- JSONB containment query using a GIN index
CREATE INDEX idx_orders_metadata ON orders USING gin (metadata);
SELECT * FROM orders WHERE metadata @> '{"priority": "high"}';
```

## Related Skills
- `dotnet.database` — engine-agnostic principles this specializes.
- `dotnet.efcore` — ORM-level query generation targeting PostgreSQL (Npgsql).
- `agentic-ai.vector-search` — `pgvector`-based retrieval for RAG.
