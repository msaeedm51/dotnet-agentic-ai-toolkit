---
id: agentic-ai.model-routing
title: Model Routing
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [model routing, choose model per task, fallback model, cheap model for simple tasks, multi-model strategy]
requires: []
related: [agentic-ai.cost-optimization, agentic-ai.reliability, agentic-ai.evaluation]
optional: [agentic-ai.frameworks.openai, agentic-ai.frameworks.anthropic, agentic-ai.frameworks.azure-openai, agentic-ai.frameworks.local-models]
prerequisites: []
tags: [model-routing, cost, agents]
---

# Model Routing

## Purpose
Route each request/step to the model that's actually appropriate for its
difficulty and requirements — not always the single most capable (and most
expensive) model available — while keeping the routing logic provider-
neutral.

## When to Use
A system with tasks/steps of varying complexity, where a simpler/cheaper
model reliably handles a meaningful fraction of them — classification,
simple extraction, or routing decisions themselves are common candidates
for a cheaper model, while complex reasoning stays on the capable one.

## Prerequisites
None, but pairs with `agentic-ai.cost-optimization` and
`agentic-ai.reliability` (routing also serves as a fallback mechanism).

## Inputs Required
The actual difficulty distribution of requests/steps, and the quality bar
each must meet (verified via the evaluation suite, not assumed).

## Engineering Principles
1. Route by task requirement, not by default — every routing decision
   should be justified by an evaluation showing the cheaper model meets the
   quality bar for that specific task type.
2. Keep routing logic behind an abstraction (`IChatClient` or equivalent)
   so the actual provider/model per route is configuration, not hardcoded
   through the calling code (framework-neutral — see
   `skills/agentic-ai/fundamentals/`).
3. Routing also serves reliability: a fallback route to a secondary
   provider/model when the primary is unavailable
   (`agentic-ai.reliability`) is the same mechanism as cost-based routing.
4. Re-evaluate routing decisions when either model changes (provider
   upgrades a model) or the task distribution shifts — a routing decision
   made once isn't permanently valid.
5. Never route a task to a model whose capability hasn't been verified
   against the evaluation suite for that specific task type — "it's cheaper
   and probably fine" is not sufficient.

## Step-by-Step Workflow
1. Classify the distinct task types/steps in the system by actual
   complexity and quality requirement.
2. For each, run the evaluation suite (`agentic-ai.evaluation`) against
   candidate models (a cheaper option vs. the default capable one) to see
   which actually meet the bar.
3. Configure routing rules mapping task type → model, gated behind the
   provider-neutral client abstraction.
4. Add a fallback route for provider unavailability
   (`agentic-ai.reliability`), distinct from cost-based routing but using
   the same mechanism.
5. Re-run the evaluation suite whenever a routed model version changes or
   the task distribution shifts meaningfully.

## Code Standards
Routing rules are explicit, reviewable configuration (a task-type → model
mapping), not implicit logic scattered across call sites choosing a model
ad hoc.

## Architecture Constraints
The calling code depends on an abstraction (`IChatClient` keyed by task
type/purpose), never a concrete provider SDK type directly — this is what
lets routing (and provider swaps) happen without touching calling code
(`skills/agentic-ai/fundamentals/` framework-neutrality note).

## Security Considerations
A fallback route to a different provider must meet the same data-handling/
compliance requirements as the primary (`agentic-ai.reliability`) — don't
silently degrade to a provider that isn't approved for the data involved.

## Testing Requirements
Each routed model is verified against the evaluation suite for its
assigned task type before being routed to in production, and re-verified
on any model version change.

## Common Mistakes
- Routing to a cheaper model without evaluation, discovering the quality
  gap from user complaints instead of the evaluation suite.
- Hardcoding a specific provider/model directly at call sites instead of
  behind an abstraction, making routing and future provider swaps expensive
  refactors.
- Not re-evaluating routing after a provider silently updates a model
  version behind the same model identifier.

## Anti-Patterns
- **Cost-only routing**: choosing the cheapest model for every task
  regardless of whether it was ever verified to meet that task's quality
  bar.
- **Hardcoded provider lock-in**: calling a specific provider's SDK type
  directly throughout the codebase instead of behind
  `IChatClient`/equivalent, making the framework-neutrality principle
  impossible to honor later.

## Validation Checklist
- [ ] Every routed model is verified against the evaluation suite for its
      task type.
- [ ] Routing logic sits behind a provider-neutral abstraction.
- [ ] A fallback route exists for provider unavailability.
- [ ] Routing is re-evaluated on model version changes.

## Definition of Done
Meets `rules/definition-of-done.md`; each route's model choice is backed
by evaluation suite results, not assumption.

## Example
```csharp
public interface IChatClientFactory
{
    IChatClient For(TaskComplexity complexity);
}

public sealed class ConfiguredChatClientFactory(IOptions<ModelRoutingOptions> options, IServiceProvider services) : IChatClientFactory
{
    public IChatClient For(TaskComplexity complexity) => complexity switch
    {
        TaskComplexity.Simple => services.GetRequiredKeyedService<IChatClient>(options.Value.SimpleModel),   // e.g. a smaller model
        TaskComplexity.Complex => services.GetRequiredKeyedService<IChatClient>(options.Value.ComplexModel), // e.g. the flagship model
        _ => throw new ArgumentOutOfRangeException(nameof(complexity))
    };
}

// Ticket classification (simple, structured) routes to a cheaper model;
// open-ended troubleshooting (complex reasoning) routes to the capable one —
// both choices backed by evaluation suite results per task type.
```

## Related Skills
- `agentic-ai.cost-optimization` — the primary driver for routing to a
  cheaper model.
- `agentic-ai.reliability` — routing as a fallback mechanism.
- `agentic-ai.evaluation` — what validates a routing decision.
