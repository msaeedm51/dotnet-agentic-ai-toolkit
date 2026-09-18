---
id: dotnet.efcore
title: Entity Framework Core
category: skill
domain: dotnet
technologies: [efcore, dotnet8, sqlserver, postgresql]
triggers: [entity framework, ef core, dbcontext, migrations, n+1, tracking, no tracking]
requires: [dotnet.csharp]
related: [dotnet.database, dotnet.performance, dotnet.architecture.repository-specification]
optional: []
prerequisites: []
tags: [efcore, orm, data-access]
---

# Entity Framework Core

## Purpose
Use EF Core correctly for the write side and simple reads: entity
configuration, migrations, tracking behavior, and query performance — and
know when to reach for something else instead.

## When to Use
- Aggregate persistence in a Clean Architecture / DDD setup.
- Straightforward CRUD and moderately complex queries.
- **Not** for bulk operations (thousands of rows), complex reporting
  queries, or a legacy schema EF can't model cleanly — use Dapper/raw SQL
  for those (see Common Mistakes).

## Prerequisites
`dotnet.csharp`.

## Inputs Required
Which database engine (SQL Server/PostgreSQL — `.ai/config.yaml`), and
whether the schema is greenfield (EF owns migrations) or existing/legacy
(EF maps to it, doesn't migrate it).

## Engineering Principles
1. Use `AsNoTracking()` for every read that doesn't need to be updated and
   saved back — tracking has real overhead and is easy to forget to disable.
2. Configure entities explicitly (`IEntityTypeConfiguration<T>`), not
   scattered data annotations mixed with fluent config.
3. One `SaveChangesAsync()` per unit of work / transaction boundary —
   don't call it multiple times across what should be one atomic operation.
4. Avoid lazy loading by default — it hides N+1 queries; use explicit
   `Include()`/projection instead.
5. Migrations are reviewed like code — a migration that locks a large table
   or drops a column needs the same scrutiny as the schema change itself
   (`dotnet.database`, `workflows/database-change.md`).
6. Compiled queries only where profiling shows they matter — not a default
   optimization.

## Step-by-Step Workflow
1. Model entities and configure them via `IEntityTypeConfiguration<T>` in a
   dedicated configuration class per entity.
2. For reads: project directly to a DTO with `Select()` +
   `AsNoTracking()` — don't load full entities just to read a few fields.
3. For writes: load the aggregate with tracking (default), mutate through
   its methods (not by setting properties directly from outside), call
   `SaveChangesAsync()` once.
4. Add a migration (`dotnet ef migrations add`), review the generated SQL,
   and check it against `workflows/database-change.md` for downtime risk
   before applying to a shared environment.
5. For anything with N+1 risk (a list of entities each needing a related
   collection), use `Include()`/`ThenInclude()` or a projection that fetches
   everything in one query — verify with logging/profiling, don't assume.

## Code Standards
- `DbContext` is scoped (default) — never injected into a singleton
  directly (`dotnet.dotnet`).
- Entity configuration lives in `IEntityTypeConfiguration<T>` classes, one
  per entity, applied via `ApplyConfigurationsFromAssembly`.
- No business logic inside `DbContext`/configuration classes.

## Architecture Constraints
`DbContext` and EF Core types never appear in Domain-layer signatures
(`dotnet.architecture.clean-architecture`); repository implementations in
Infrastructure are the only place EF Core is referenced directly.

## Security Considerations
LINQ-to-Entities parameterizes queries automatically — never drop to raw
SQL with string-concatenated input (`FromSqlRaw` with interpolated user
input is a SQL injection vector; use `FromSqlInterpolated` or parameters).

## Testing Requirements
Integration-test against a real database engine (Testcontainers) for
anything relying on engine-specific behavior or query translation — EF's
in-memory provider doesn't enforce real constraints and can pass tests that
fail against the real database.

## Common Mistakes
- Forgetting `AsNoTracking()` on read-only queries, adding unnecessary
  change-tracking overhead at scale.
- Triggering N+1 by accessing a navigation property in a loop without
  `Include()`, especially with lazy loading enabled.
- Using EF Core for a bulk update/delete across many rows — issues one
  round-trip per entity by default; use `ExecuteUpdateAsync`/
  `ExecuteDeleteAsync` (EF Core 7+) or raw SQL for bulk operations.
- Testing against the in-memory provider only, missing real-database
  constraint violations and translation failures.

## Anti-Patterns
- **Entity as DTO**: returning the tracked entity straight from an API
  endpoint, coupling the wire contract to the schema.
- **God DbContext**: one `DbContext` spanning every module in a modular
  monolith, defeating module boundary enforcement
  (`dotnet.architecture.modular-monolith`).
- **EF Core for everything**: forcing a complex reporting query or bulk
  import through LINQ when raw SQL/Dapper is clearer and faster.

## Validation Checklist
- [ ] Read-only queries use `AsNoTracking()` and project to DTOs.
- [ ] No N+1 pattern in a loop over navigation properties.
- [ ] Migrations reviewed for downtime/locking risk before applying to a
      shared environment.
- [ ] Raw SQL, if used, is parameterized — never string-concatenated.

## Definition of Done
Meets `rules/definition-of-done.md`; new queries verified against a real
database engine, not only the in-memory provider.

## Example
```csharp
public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);
        builder.Property(o => o.Id).HasConversion(id => id.Value, value => new OrderId(value));
        builder.OwnsMany(o => o.Lines, lines => lines.WithOwner());
        builder.Property(o => o.Status).HasConversion<string>();
    }
}

// Read: no-tracking projection, no N+1
var summaries = await db.Orders.AsNoTracking()
    .Where(o => o.CustomerId == customerId)
    .Select(o => new OrderSummary(o.Id.Value, o.Status.ToString(), o.Lines.Count))
    .ToListAsync(ct);

// Write: load tracked, mutate through the aggregate, save once
var order = await db.Orders.Include(o => o.Lines).FirstOrDefaultAsync(o => o.Id == orderId, ct);
order!.Submit();
await db.SaveChangesAsync(ct);
```

## Related Skills
- `dotnet.database` — engine-specific detail (SQL Server/PostgreSQL).
- `dotnet.performance` — query/allocation performance tuning.
- `dotnet.architecture.repository-specification` — repository pattern
  wrapping EF Core.
