---
id: dotnet.performance
title: Performance (Allocations, Async, Scalability)
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore]
triggers: [performance, allocations, garbage collection, async performance, scalability, profiling]
requires: []
related: [dotnet.caching, dotnet.database, dotnet.dotnet]
optional: []
prerequisites: []
tags: [performance]
---

# Performance (Allocations, Async, Scalability)

## Purpose
Diagnose and fix real performance problems with evidence — profiling,
benchmarks, execution plans — rather than speculative micro-optimization.

## When to Use
A stated performance symptom (slow endpoint, high memory, CPU spike) or a
request to optimize a specific hot path. Not a default pass over working
code with no reported problem.

## Prerequisites
None.

## Inputs Required
The actual symptom and, ideally, profiling/timing data. If none exists,
help gather it before proposing a fix (`agent.performance-engineer`).

## Engineering Principles
1. Measure before optimizing — a change without a before/after measurement
   is a guess, not a fix.
2. Async for I/O-bound work; never block on async (`.Result`/`.Wait()`) —
   causes thread-pool starvation under load even when it "works" in
   development.
3. Avoid unnecessary allocations in hot paths — `Span<T>`/`Memory<T>` where
   profiling shows GC pressure matters; don't reach for these by default in
   cold paths where clarity matters more.
4. Avoid `async`/`await` overhead on trivial synchronous work called in a
   tight loop — not every method needs to be async.
5. Scale-test assumptions: what works at 10 requests/sec may not at 1000 —
   identify what actually breaks under load (connection pool exhaustion,
   lock contention, N+1 queries) rather than assuming more hardware fixes
   it.

## Step-by-Step Workflow
1. Reproduce the symptom, or get timing/profiler data from the user if it
   can't be reproduced locally.
2. Profile (dotnet-trace, a memory dump, or targeted `Stopwatch`/
   `BenchmarkDotNet` measurement) to find the actual bottleneck — don't
   guess.
3. Check the usual suspects first: N+1 queries (`dotnet.efcore`), missing
   `AsNoTracking()`, `new HttpClient()` per call, synchronous-over-async,
   unnecessary allocations in a loop.
4. Apply the targeted fix; re-measure to confirm it actually improved the
   metric that mattered.
5. If no measurement is possible in this environment, say so explicitly
   rather than claiming an unverified improvement.

## Code Standards
No `.Result`/`.Wait()` on the request path. `HttpClient` from
`IHttpClientFactory`. `AsNoTracking()` on read-only EF Core queries.
`CancellationToken` propagated so a client disconnect actually frees server
resources.

## Architecture Constraints
A performance fix should not change observable behavior beyond speed —
flag it explicitly if it must.

## Security Considerations
Caching a response that varies by user/authorization must key the cache
correctly (never serve one user's cached data to another) —
`dotnet.caching`.

## Testing Requirements
A `BenchmarkDotNet` micro-benchmark for a hot-path change where the
improvement claim needs to be defensible; a regression test for correctness
(the optimization didn't change behavior).

## Common Mistakes
- Optimizing a path that isn't actually the bottleneck because it's the
  easiest one to change.
- Adding caching to "fix" a slow query instead of fixing the query, masking
  the real problem and adding staleness risk.
- Assuming `async` alone makes code faster — it improves throughput/
  scalability under concurrent load, not single-call latency.

## Anti-Patterns
- **Premature optimization**: rewriting clear code into a "faster" but
  harder-to-read form with no evidence it was ever a bottleneck.
- **Cargo-cult async**: making every method `async` even when it does no
  I/O, adding state-machine overhead for no benefit.

## Validation Checklist
- [ ] The bottleneck is confirmed by profiling/measurement, not assumed.
- [ ] The fix is measured before/after where feasible.
- [ ] No blocking-on-async introduced or left in place.
- [ ] Behavior is unchanged except for the measured performance
      characteristic.

## Definition of Done
Meets `rules/definition-of-done.md`; the performance claim is backed by a
measurement, or explicitly labeled unverified if measurement wasn't
possible in this environment.

## Example
```csharp
// Before: blocks a thread-pool thread per call, doesn't scale under load
public OrderSummary GetSummary(Guid id) => _repository.FindAsync(id).Result;

// After: genuinely async all the way, scales with concurrent load
public Task<OrderSummary?> GetSummaryAsync(Guid id, CancellationToken ct) =>
    _repository.FindAsync(id, ct);
```

## Related Skills
- `dotnet.caching` — caching as a targeted mitigation, not a default fix.
- `dotnet.database` — query-level performance root causes.
- `agentic-ai.cost-optimization` / `agentic-ai.model-routing` — the
  agentic-AI-track equivalent of this skill for token cost/latency.
