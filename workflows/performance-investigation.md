---
id: workflow.performance-investigation
title: Performance Investigation
category: workflow
triggers: [this is slow, investigate performance, why is this slow, optimize this]
agents_involved: [agent.performance-engineer, agent.database-engineer, agent.test-engineer]
skills_loaded: [dotnet.performance]
tags: [performance, investigation]
---

# Performance Investigation

## Purpose
Root-cause a performance problem with evidence before fixing it — the
performance-specific variant of `workflows/bug-fix.md`'s discipline,
substituting measurement for reproduction-by-symptom.

## When to Use
A stated performance symptom: slow endpoint, high latency, high resource
usage, timeout under load.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-3 | `agent.performance-engineer` | Symptom | Profiling data | Step 4 |
| 4 | `agent.performance-engineer` / `agent.database-engineer` | Profiling data | Root cause | Step 5 |
| 5 | `agent.performance-engineer` | Root cause | Fix | Step 6 |
| 6 | `agent.test-engineer` | Fix | Benchmark/regression test | End |

## Stages

### 1. Symptom
- **Actions:** Get a precise statement of the symptom: what's slow,
  compared to what expectation, under what conditions.
- **Output:** Precise symptom statement.
- **Gate:** None.

### 2. Reproduce or gather data
- **Actions:** Reproduce locally if feasible, or request profiling/timing
  data from the user (`AGENTS.md` §2) if not.
- **Output:** Reproduction or real data to analyze.
- **Gate:** Some form of evidence exists before hypothesizing — not
  guessing from the symptom description alone.

### 3. Profile
- **Actions:** Identify the actual bottleneck via profiling/execution
  plans/timing data — the usual suspects: N+1 queries, missing
  `AsNoTracking()`, blocking-on-async, unnecessary allocations, missing
  resilience causing retries/timeouts.
- **Output:** Identified bottleneck, backed by evidence.
- **Gate:** The bottleneck is confirmed by data, not assumed from
  intuition (`dotnet.performance`).

### 4. Root cause
- **Actions:** For a database-related bottleneck, involve
  `agent.database-engineer` for execution-plan-level analysis.
- **Output:** Confirmed root cause.
- **Gate:** Root cause is specific and evidenced (e.g. "query X causes a
  table scan due to missing index Y," not "the database seems slow").

### 5. Fix
- **Actions:** Apply the targeted fix for the confirmed root cause.
- **Output:** Fix.
- **Gate:** Fix directly addresses the confirmed cause; no unrelated
  change bundled in.

### 6. Measure and validate
- **Actions:** Re-measure the same metric that was originally slow, using
  the same method as the original measurement, to confirm improvement. Add
  a benchmark or regression test where the improvement claim needs to be
  defensible over time.
- **Output:** Before/after measurement; regression test.
- **Gate:** The fix is confirmed to have improved the measured metric; if
  measurement isn't possible in this environment, this is stated explicitly
  rather than claiming an unverified improvement (`rules/performance.md`).

## Escalation
If the bottleneck turns out to require an architectural change (e.g. a
synchronous chain that needs to become async end-to-end, or a service
split), escalate to `agent.architect` rather than applying a local
workaround that doesn't address the structural cause.

## Related Workflows
- `workflows/bug-fix.md` — the general debugging discipline this
  specializes.
- `workflows/database-change.md` — if the fix requires a schema/index
  change.
