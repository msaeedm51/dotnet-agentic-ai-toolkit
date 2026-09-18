---
id: prompt.review.performance-review
title: Performance Review
category: prompt
domain: dotnet
related_skills: [dotnet.performance]
related_agents: [agent.performance-engineer]
tags: [review, performance]
---

# Performance Review

## Purpose
Flag performance risk in a diff with evidence, not speculation — the
review-time counterpart to a full `workflows/performance-investigation.md`.

## When to Use
Reviewing a diff that touches a database query, a loop over external data,
a hot path, or a new outbound dependency.

## Required Context
The diff, and — where possible — profiling/timing data or an execution
plan.

## Prompt

```
Review [DIFF] for performance risk, per dotnet.performance and
rules/performance.md.

Check specifically for: N+1 query patterns, missing AsNoTracking() on
read-only queries, blocking-on-async (.Result/.Wait()), missing
CancellationToken propagation, unbounded result sets with no pagination,
new HttpClient() instead of HttpClientFactory, and any outbound call with
no timeout/resilience policy.

For each finding, state the concrete scenario where it degrades
performance (not just "this could be slow"), and whether it's measurable
now or needs to be flagged for follow-up measurement.
```

## Expected Output
A list of concrete, evidenced performance findings (or a clean bill if
none apply) — never a speculative "consider optimizing this" without a
specific mechanism.

## Related Skills / Agents
`agent.performance-engineer` executes; escalate to
`agent.database-engineer` for query/index-level findings.
