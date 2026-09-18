---
id: agentic-ai.fundamentals.planning
title: Planning
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [task planning, decompose task, plan and execute, agent planning]
requires: []
related: [agentic-ai.fundamentals.agent-loops, agentic-ai.fundamentals.multi-agent-systems, agentic-ai.evaluation]
optional: []
prerequisites: [agentic-ai.fundamentals.agent-loops]
tags: [agents, planning]
---

# Planning

## Purpose
Decide when a task needs an explicit up-front plan (decomposed into steps
before execution starts) versus a purely reactive agent loop that decides
its next action one step at a time — and how to implement plan-then-execute
when it's the right fit.

## When to Use
- The task has a natural multi-step structure that benefits from being
  made explicit and reviewable (especially before any irreversible action).
- You want to validate/show the plan (to a user, or a guardrail check)
  before execution begins.
- Not needed for simple, few-step tasks where the reactive loop
  (`agentic-ai.fundamentals.agent-loops`) already handles sequencing fine —
  planning adds a call and complexity that must earn its keep.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`.

## Inputs Required
Whether the task benefits from plan review/approval before execution (a
concrete driver: cost, risk, or a human-in-the-loop requirement), or
whether reactive step-by-step is sufficient.

## Engineering Principles
1. Plan-then-execute: generate a structured plan (a sequence of steps, each
   with its intended tool/action) with one model call, then execute each
   step, optionally re-planning if a step's result invalidates the rest of
   the plan.
2. A plan is a structured output (`agentic-ai.structured-outputs`), not
   free-text the executor has to re-parse loosely.
3. Re-planning (updating the plan mid-execution based on new information)
   is itself a deliberate decision point, not automatic after every step —
   define when it triggers.
4. A reviewable plan is valuable specifically because it's a checkpoint —
   pair it with `agentic-ai.human-in-the-loop` for anything where showing
   the plan before acting has real value (cost, risk, irreversibility).

## Step-by-Step Workflow
1. Decide if this task needs explicit planning (see When to Use) — default
   to the simpler reactive loop if unsure.
2. Prompt the model for a structured plan: ordered steps, each naming an
   intended action/tool and its purpose.
3. Validate the plan against guardrails (`agentic-ai.guardrails`) — does
   any step require human approval, exceed a cost/risk bound, or use a tool
   not actually available.
4. Execute each step, feeding results into context for subsequent steps.
5. If a step's result contradicts an assumption the plan depended on,
   trigger re-planning rather than blindly continuing a now-invalid plan.

## Code Standards
The plan type is a structured, strongly-typed model (a list of typed step
records), not a raw string parsed with regex.

## Architecture Constraints
Planning and execution are separable — the plan step's output should be
inspectable/loggable independent of execution, so a plan can be reviewed,
tested, or replayed.

## Security Considerations
A generated plan is not automatically trustworthy just because it's
structured — validate that every planned tool call is one the agent is
actually authorized to make before executing it (`agentic-ai.ai-security`).

## Testing Requirements
Evaluation cases asserting the plan generated for a known task matches the
expected step sequence (or at least uses the expected tools), plus cases
where re-planning should trigger and cases where it shouldn't.

## Common Mistakes
- Adding a planning step to every task regardless of complexity, adding
  latency and cost with no benefit for simple cases.
- Treating the plan as immutable even when a step's result clearly
  invalidates a later step.
- Parsing a free-text plan with fragile string matching instead of
  requesting structured output.

## Anti-Patterns
- **Plan theater**: generating a plan that's shown to the user but not
  actually what the executor follows — the displayed plan and actual
  behavior diverge.
- **Infinite re-planning**: re-planning after every single step regardless
  of whether anything actually changed, effectively turning plan-then-
  execute back into an expensive reactive loop.

## Validation Checklist
- [ ] Planning is used only where it adds real value over a reactive loop.
- [ ] The plan is structured output, not free text.
- [ ] Every planned tool call is validated against actual authorization
      before execution.
- [ ] Re-planning triggers on a defined condition, not arbitrarily.

## Definition of Done
Meets `rules/definition-of-done.md`; evaluation cases cover both a
straightforward plan and a re-planning scenario.

## Example
```csharp
public sealed record PlanStep(int Order, string Tool, string Purpose);
public sealed record Plan(IReadOnlyList<PlanStep> Steps);

var plan = await model.GetStructuredResponseAsync<Plan>(
    $"Break down this task into tool-calling steps: {task}", ct);

foreach (var step in plan.Steps.OrderBy(s => s.Order))
{
    if (!toolRegistry.IsAuthorized(step.Tool, currentContext))
        return AgentResult.Failure($"Plan references unauthorized tool: {step.Tool}");

    var result = await ExecuteStepAsync(step, ct);
    if (result.InvalidatesPlan)
        plan = await ReplanAsync(task, executedSoFar: plan, newInfo: result, ct);
}
```

## Related Skills
- `agentic-ai.fundamentals.agent-loops` — the simpler default this extends.
- `agentic-ai.structured-outputs` — how the plan itself is generated.
- `agentic-ai.human-in-the-loop` — reviewing a plan before execution.
