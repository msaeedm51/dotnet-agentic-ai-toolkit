---
id: rule.performance
title: Performance Rules
category: rule
tech_tags: [dotnet, aspnetcore]
triggers: [performance rules, allocation rule, async rule performance, caching rule]
severity: recommended
tags: [performance]
---

# Performance Rules

## Measure before optimizing

**Rule:** A performance change is backed by a profiling/benchmark
measurement identifying the actual bottleneck — not applied speculatively
to code that "looks slow."

**Why:** Optimizing the wrong thing wastes effort and adds complexity with
no measured benefit.

**Applies to:** Every performance-motivated change.

**Exception:** A change with an obviously correct, low-risk fix (e.g.
adding a missing `AsNoTracking()`) where the reasoning is self-evident.

---

## Never block on async on a request/concurrency-sensitive path

**Rule:** See `rules/csharp.md` — restated here as a performance rule since
this is one of the most common causes of thread-pool starvation under load.

**Why:** This is a correctness rule and a performance rule simultaneously —
violating it degrades throughput under exactly the load conditions that
matter most.

**Applies to:** Every async call on a request-handling path.

**Exception:** See `rules/csharp.md`.

---

## Cache only with a designed invalidation strategy

**Rule:** Caching is added only after invalidation is designed
(`dotnet.caching`) — never as a reflexive fix for a slow query without
addressing the actual query.

**Why:** A cache without designed invalidation trades a performance problem
for a correctness/staleness problem, which is often worse.

**Applies to:** Every new cache.

**Exception:** None.

---

## Avoid N+1 query patterns

**Rule:** Accessing a navigation/related collection in a loop is checked
for N+1 — use `Include()`/projection to fetch related data in one query
instead.

**Why:** N+1 queries work fine with a handful of rows in development and
degrade severely as data grows.

**Applies to:** Any loop touching related/navigation data.

**Exception:** None.

---

## Outbound HTTP calls have a resilience policy

**Rule:** Every outbound HTTP dependency has an explicit timeout, and
retry/circuit-breaker policy appropriate to its criticality
(`dotnet.dotnet`).

**Why:** An unbounded outbound call can hang a request indefinitely and
cascade into an outage of the calling service too.

**Applies to:** Every outbound HTTP dependency.

**Exception:** None.

---

## A performance fix does not change observable behavior

**Rule:** A change made for performance reasons produces the same
observable output as before, unless the behavior change is explicit and
separately justified.

**Why:** Silently trading correctness for speed (e.g. dropping a validation
check) is not a valid performance optimization.

**Applies to:** Every performance-motivated change.

**Exception:** None.
