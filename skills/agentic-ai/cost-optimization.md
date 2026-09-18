---
id: agentic-ai.cost-optimization
title: Cost Optimization
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [token cost, reduce llm cost, cost per request, budget agent, expensive prompts]
requires: []
related: [agentic-ai.model-routing, agentic-ai.context-engineering, agentic-ai.observability]
optional: []
prerequisites: [agentic-ai.observability]
tags: [cost, performance, agents]
---

# Cost Optimization

## Purpose
Keep token/API cost predictable and bounded per request and in aggregate —
the agentic-AI-track equivalent of `dotnet.performance`, applied to a cost
model that's directly proportional to tokens processed, not just latency.

## When to Use
Any production agentic-AI feature — cost is a first-class constraint here,
not an afterthought, because unlike most application code, every request
has a direct, measurable dollar cost that scales with usage.

## Prerequisites
`agentic-ai.observability` — you need token/cost telemetry before you can
optimize it.

## Inputs Required
The actual cost budget per request/feature (from the project), and current
token usage broken down by component (system prompt, context, tool
results, output).

## Engineering Principles
1. Measure before optimizing — same discipline as `dotnet.performance`;
   know where tokens are actually going before cutting them.
2. Context size is the biggest lever — trim what's in context deliberately
   (`agentic-ai.context-engineering`) before reaching for a cheaper model.
3. Route to the cheapest model that reliably handles the task
   (`agentic-ai.model-routing`) — not every step needs the most capable/
   expensive model.
4. Cache and reuse where correctness allows (identical or near-identical
   requests, provider-level prompt caching for stable system prompts) —
   many providers discount cached/repeated prompt prefixes.
5. Set a hard per-request and aggregate (daily/monthly) cost bound with
   alerting — a bug in a loop shouldn't be discovered via the bill.

## Step-by-Step Workflow
1. Break down current token usage by component using observability data
   (`agentic-ai.observability`): system prompt, conversation history,
   retrieved/tool content, output.
2. Identify the largest contributor and whether it's actually necessary at
   that size — trim context first (cheapest, no quality trade-off if done
   right).
3. Evaluate whether every step needs the most capable model, or whether
   model routing can shift simpler steps to a cheaper model without hurting
   quality (verify with the evaluation suite,
   `agentic-ai.evaluation`).
4. Apply provider-level prompt caching for stable, reused prefixes (system
   prompts, few-shot examples) where the provider supports it.
5. Set and alert on a per-request and aggregate cost bound; treat a bound
   breach as an incident to investigate, not just a number to note.

## Code Standards
Cost/token budgets are explicit constants/configuration values, checked in
code (e.g. rejecting a context assembly that exceeds the budget), not just
documented targets nobody enforces.

## Architecture Constraints
Cost-optimization changes (model routing, context trimming) must not
silently degrade correctness — verify against the evaluation suite before
and after (`agentic-ai.evaluation`), the same discipline
`dotnet.performance` requires for a performance change that touches
behavior.

## Security Considerations
Don't cache/reuse content across requests in a way that leaks one user's
data into another's cached response — cache keys must respect the same
scoping rules as `dotnet.caching`.

## Testing Requirements
A cost-optimization change (model routing, context trimming) is evaluated
against the same evaluation suite the original implementation used, to
confirm no quality regression, plus a direct measurement of the actual cost
reduction.

## Common Mistakes
- Optimizing model choice before optimizing context size — often the
  bigger lever and free of quality trade-offs.
- Routing a task to a cheaper model without evaluating whether it still
  meets the quality bar, discovering the regression from user complaints
  instead of the evaluation suite.
- No aggregate cost alerting, so a runaway loop or unexpected traffic
  pattern is discovered via the monthly bill.

## Anti-Patterns
- **Optimize blind**: cutting context or switching models without
  measuring the actual token breakdown first, guessing at what's expensive.
- **Cost at any quality cost**: routing everything to the cheapest model
  without verifying it still meets the task's actual quality bar.

## Validation Checklist
- [ ] Token usage is broken down by component before optimizing.
- [ ] Context is trimmed to what's actually needed before considering model
      downgrade.
- [ ] Model routing changes are verified against the evaluation suite.
- [ ] A per-request and aggregate cost bound exists with alerting.

## Definition of Done
Meets `rules/definition-of-done.md`; a cost-optimization change reports
both the measured cost reduction and evaluation suite results (no
regression).

## Example
```csharp
public sealed class CostBudgetGuard(int maxInputTokensPerRequest, decimal maxCostPerRequestUsd)
{
    public void Enforce(TokenUsageEstimate estimate)
    {
        if (estimate.InputTokens > maxInputTokensPerRequest)
            throw new CostBudgetExceededException($"Input {estimate.InputTokens} tokens exceeds budget {maxInputTokensPerRequest}.");

        if (estimate.EstimatedCostUsd > maxCostPerRequestUsd)
            throw new CostBudgetExceededException($"Estimated cost ${estimate.EstimatedCostUsd} exceeds budget ${maxCostPerRequestUsd}.");
    }
}
```

## Related Skills
- `agentic-ai.model-routing` — routing to the cheapest sufficient model.
- `agentic-ai.context-engineering` — the biggest cost lever.
- `agentic-ai.observability` — the telemetry this skill depends on.
