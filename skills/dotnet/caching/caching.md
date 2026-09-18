---
id: dotnet.caching
title: Caching (In-Memory, Distributed, Output)
category: skill
domain: dotnet
technologies: [aspnetcore, redis]
triggers: [caching, distributed cache, output caching, cache invalidation, memory cache]
requires: []
related: [dotnet.performance, dotnet.dotnet]
optional: []
prerequisites: []
tags: [caching, performance]
---

# Caching (In-Memory, Distributed, Output)

## Purpose
Reduce load and latency for data that's expensive to compute/fetch and
tolerant of some staleness — with invalidation designed up front, since
that's where caching actually goes wrong.

## When to Use
Data read far more often than it changes, expensive to compute/fetch, and
where some staleness window is acceptable. Not a substitute for fixing an
actually-slow query (`dotnet.performance`).

## Prerequisites
None.

## Inputs Required
The acceptable staleness window, and whether the data varies per user/
tenant (affects cache key design).

## Engineering Principles
1. Design invalidation before adding the cache — "how does this entry get
   removed/updated when the source changes" is the hard part, not the
   lookup.
2. In-memory (`IMemoryCache`) for single-instance or per-instance-tolerable
   data; distributed (`IDistributedCache`, Redis) when multiple instances
   must share a consistent cache view.
3. Output caching (ASP.NET Core's `OutputCache`) for whole-response caching
   of GET endpoints with no per-user variation, or explicit vary-by rules
   when there is.
4. Cache keys include every dimension the value varies by (user, tenant,
   locale) — a missing dimension leaks one user's data to another.
5. Set an expiration on every cache entry — an unbounded cache is a memory
   leak waiting to happen.

## Step-by-Step Workflow
1. Confirm the data is actually a good caching candidate (read-heavy,
   expensive, staleness-tolerant) — if not, don't cache it.
2. Design the cache key including every varying dimension.
3. Choose in-memory vs. distributed based on whether instances must share a
   view.
4. Set an explicit expiration (absolute and/or sliding) appropriate to the
   staleness tolerance.
5. Design invalidation: on write, either evict the specific key or use a
   short enough expiration that staleness is acceptable without explicit
   invalidation.
6. For output caching, define vary-by rules (query string, header, user) so
   the cache doesn't serve one user's response to another.

## Code Standards
Cache key construction is centralized (a method/builder), not
string-concatenated ad hoc at every call site, to avoid key-format drift
causing cache misses or, worse, collisions.

## Architecture Constraints
Caching is an infrastructure concern — cache access lives behind an
interface the application layer calls, so it can be swapped/disabled
without changing business logic.

## Security Considerations
Never cache a response containing authorization-sensitive data under a key
that doesn't include the identity/permission context — this is a concrete
way to leak one user's data to another (`dotnet.security`).

## Testing Requirements
Test invalidation explicitly: writing new data and confirming a subsequent
read reflects it within the expected window, not just that caching
"speeds things up."

## Common Mistakes
- Caching per-user data under a key that doesn't include the user id.
- No expiration set, causing unbounded growth in `IMemoryCache`.
- Adding caching before confirming invalidation is even feasible for the
  data's write pattern.

## Anti-Patterns
- **Cache as a query-performance bandaid**: caching a slow query's result
  instead of fixing the query, hiding the real problem and adding
  staleness risk on top.
- **Stampede-prone cache**: many concurrent requests all missing the cache
  at once and all recomputing the same expensive value simultaneously —
  needs a lock/single-flight pattern for hot keys.

## Validation Checklist
- [ ] Cache key includes every dimension the value varies by.
- [ ] Every entry has an explicit expiration.
- [ ] Invalidation is designed, not assumed to "just expire eventually"
      when correctness requires fresher data.
- [ ] Distributed cache used when multiple instances must share state.

## Definition of Done
Meets `rules/definition-of-done.md`; invalidation behavior is covered by a
test.

## Example
```csharp
public sealed class CachedOrderSummaryReader(IDistributedCache cache, AppDbContext db)
{
    public async Task<OrderSummary?> GetAsync(Guid customerId, Guid orderId, CancellationToken ct)
    {
        var key = $"order-summary:{customerId}:{orderId}"; // includes owning user
        var cached = await cache.GetStringAsync(key, ct);
        if (cached is not null)
            return JsonSerializer.Deserialize<OrderSummary>(cached);

        var summary = await db.Orders.AsNoTracking()
            .Where(o => o.Id == orderId && o.CustomerId == customerId)
            .Select(o => new OrderSummary(o.Id, o.Status.ToString(), o.Total))
            .FirstOrDefaultAsync(ct);

        if (summary is not null)
            await cache.SetStringAsync(key, JsonSerializer.Serialize(summary),
                new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5) }, ct);

        return summary;
    }
}
```

## Related Skills
- `dotnet.performance` — when caching is (and isn't) the right fix.
- `dotnet.dotnet` — output caching middleware configuration.
