---
id: agentic-ai.fundamentals.multi-agent-systems
title: Multi-Agent Systems
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [multi-agent, agent orchestration, agent handoff, supervisor agent, agent-to-agent]
requires: []
related: [agentic-ai.fundamentals.agent-loops, agentic-ai.fundamentals.planning, agentic-ai.observability]
optional: [agentic-ai.frameworks.microsoft-agent-framework, agentic-ai.frameworks.semantic-kernel]
prerequisites: [agentic-ai.fundamentals.agent-loops]
tags: [agents, multi-agent, orchestration]
---

# Multi-Agent Systems

## Purpose
Split a task across multiple specialized agents (each with a narrower
scope, tool set, and prompt) when a single agent's scope has become
unwieldy — and know when that split is adding coordination overhead
instead of clarity.

## When to Use
- The task has genuinely distinct sub-domains, each better served by a
  focused agent with its own tools/context than one generalist agent
  juggling everything.
- Not a default architecture — most tasks are solved fine by a single
  well-scoped agent loop; multi-agent adds coordination complexity,
  latency, and cost that must be justified by an actual scope problem.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`.

## Inputs Required
The specific reason a single agent isn't sufficient (context window
pressure from too many tools, genuinely distinct expertise domains, or a
need for independent evaluation/guardrails per sub-domain).

## Engineering Principles
1. Each agent has a narrow, well-defined responsibility and tool set —
   mirroring this toolkit's own agent design (`agents/*.md`): specialized,
   not overlapping.
2. Coordination pattern is explicit and simple: a supervisor/orchestrator
   agent routing to specialists (hub-and-spoke) is usually easier to reason
   about and debug than free-form agent-to-agent negotiation.
3. Handoffs pass structured context (`agentic-ai.structured-outputs`), not
   an unstructured conversation dump — the receiving agent gets exactly
   what it needs, not everything the previous agent saw.
4. Each agent's step/cost bounds are independent, but the overall system
   has an aggregate bound too — five agents each with a generous budget can
   still blow the total cost/latency budget.
5. Observability spans the whole multi-agent run (a single correlation id),
   not just each agent in isolation — debugging requires seeing the full
   handoff chain.

## Step-by-Step Workflow
1. Confirm a single agent genuinely can't serve the task well (see When to
   Use) — escalate to `agent.architect` if this is a new system design
   decision, not just an implementation choice.
2. Define each specialist agent's scope, tools, and prompt narrowly.
3. Choose a coordination pattern: supervisor routing to specialists is the
   default; peer-to-peer negotiation only if the task genuinely needs it
   (rare, and harder to make reliable).
4. Define the handoff contract: what structured data moves from one agent
   to the next.
5. Set an aggregate bound (total cost/steps/time across the whole
   multi-agent run), not just per-agent bounds.
6. Instrument with one correlation id across the whole run for
   observability (`agentic-ai.observability`).

## Code Standards
Each agent is its own class/service with its own tool registry and system
prompt — not one giant class with conditional logic branching on "which
agent am I right now."

## Architecture Constraints
The supervisor/orchestrator is itself bound (max hops between agents, not
just max steps within one agent) — an orchestration that can bounce between
two agents indefinitely is as dangerous as an unbounded single-agent loop.

## Security Considerations
A specialist agent's tool access is scoped to its actual responsibility —
don't give every agent in the system every tool "for convenience"; that
defeats the isolation benefit and widens the blast radius of a
prompt-injection-induced bad action (`agentic-ai.ai-security`).

## Testing Requirements
Evaluation cases covering: correct routing to the right specialist for a
given task, a handoff carrying the correct structured context, and the
aggregate bound triggering gracefully when hit.

## Common Mistakes
- Splitting into multiple agents before establishing that a single agent
  actually can't handle the scope — premature complexity.
- No aggregate cost/step bound across the whole multi-agent run, only
  per-agent bounds.
- Passing the entire conversation history to every agent in a handoff
  instead of a scoped, structured handoff payload.

## Anti-Patterns
- **Agent sprawl**: many overlapping agents with unclear boundaries, so
  it's unclear which one should handle a given request.
- **Chatty orchestration**: agents bouncing a task back and forth many
  times with no forward progress, burning cost/latency with no aggregate
  bound to stop it.

## Validation Checklist
- [ ] A genuine scope problem justifies the multi-agent split (documented).
- [ ] Each agent's tool access is scoped to its responsibility.
- [ ] Handoffs use structured, minimal context — not a full history dump.
- [ ] An aggregate bound exists across the whole multi-agent run.
- [ ] One correlation id traces the full run for observability.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; evaluation
covers routing correctness and the aggregate bound.

## Example
```csharp
public sealed record HandoffContext(string Summary, IReadOnlyDictionary<string, object> Data);

public sealed class SupervisorAgent(IReadOnlyDictionary<string, ISpecialistAgent> specialists)
{
    private const int MaxHops = 6;

    public async Task<AgentResult> RunAsync(string task, CancellationToken ct)
    {
        var hops = 0;
        var context = new HandoffContext(task, new Dictionary<string, object>());

        while (hops++ < MaxHops)
        {
            var route = await DecideRouteAsync(context, ct); // which specialist next, or done
            if (route.IsDone) return AgentResult.Success(route.FinalAnswer!);

            context = await specialists[route.SpecialistName].HandleAsync(context, ct);
        }

        return AgentResult.BoundExceeded(hops: MaxHops);
    }
}
```

## Related Skills
- `agentic-ai.fundamentals.agent-loops` — the single-agent building block.
- `agentic-ai.fundamentals.planning` — plan-based coordination alternative.
- `agentic-ai.observability` — tracing a multi-agent run end to end.
