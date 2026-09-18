---
id: agentic-ai.fundamentals.agent-loops
title: Agent Loops
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [agent loop, tool use loop, react pattern, autonomous agent, think act observe]
requires: [dotnet.dotnet]
related: [agentic-ai.tool-calling, agentic-ai.context-engineering, agentic-ai.reliability, agentic-ai.fundamentals.planning]
optional: [agentic-ai.frameworks.semantic-kernel, agentic-ai.frameworks.microsoft-agent-framework]
prerequisites: []
tags: [agents, agent-loop, react]
---

# Agent Loops

## Purpose
Define the core "agent" primitive: a loop that lets an LLM reason, call
tools, observe results, and repeat until it reaches a final answer or hits
a bound — implemented concept-first in .NET, before considering any
specific framework.

## When to Use
The task needs the model to take multiple steps, call tools, and decide
what to do next based on results — not a single prompt-in, text-out call.
Not every LLM feature needs a loop; a single structured-output call
(`agentic-ai.structured-outputs`) is simpler and should be preferred when
one round trip suffices.

## Prerequisites
None, but `dotnet.dotnet` (hosting/DI/background-processing) for the
implementation.

## Inputs Required
The tools the agent needs access to, a hard bound on steps/cost/time, and
what "done" looks like (a final-answer signal, a specific tool call, or a
step limit).

## Engineering Principles
1. The loop is bounded, always: max steps, max tokens/cost, and a timeout
   — an unbounded loop is a production incident waiting to happen
   (`rules/agentic-ai.md`).
2. Every loop iteration is: model call → parse response → if tool call(s),
   execute and feed results back; if final answer, stop.
3. Tool results are appended to context as observations, not silently
   discarded — but see `agentic-ai.context-engineering` for how much of a
   large tool result actually belongs in context.
4. Treat tool output as untrusted data when it's fed back into the prompt
   — it must not be interpreted as a new instruction from the user/system
   (`agentic-ai.ai-security`).
5. Log every step (model call, tool call + result, decision) for
   observability and evaluation — an agent that "just didn't work" with no
   trace is undebuggable (`agentic-ai.observability`).
6. Design the loop pattern (concept) independent of any specific SDK —
   implement directly against the model provider's API first; a framework
   (`agentic-ai.frameworks.*`) is an optional accelerant, not the
   foundation.

## Step-by-Step Workflow
1. Define the bound: max steps (e.g. 10), max tokens/cost per run, and a
   wall-clock timeout.
2. Define the tool set the agent can call (`agentic-ai.tool-calling`) and
   the termination condition (a specific "final answer" tool/signal, or the
   model choosing not to call a tool).
3. Implement the loop: call the model with the conversation + tool
   definitions; if it requests a tool call, execute it (with its own
   timeout) and append the result as an observation; repeat.
4. On bound exceeded, terminate gracefully with a defined fallback (return
   partial progress, ask the user for guidance, or fail explicitly) — never
   let the caller wait indefinitely.
5. Log each step for observability; build an evaluation harness
   (`agentic-ai.evaluation`) covering expected tool-call sequences for
   representative tasks.
6. Only after this works with the raw provider API, consider whether a
   framework (`agentic-ai.frameworks.*`) reduces boilerplate enough to
   justify the added dependency — gated by `.ai/config.yaml` →
   `ai.frameworks`.

## Code Standards
The loop's step limit, timeout, and cost bound are explicit constants/
configuration, not implicit ("it usually stops after a few steps").

## Architecture Constraints
The agent loop lives in the agentic-ai implementation layer and calls into
`dotnet` application services through the same ports/interfaces any other
caller would use (`dotnet.architecture.clean-architecture`) — it doesn't
bypass authorization or validation that would apply to a human-initiated
equivalent action.

## Security Considerations
Every tool the loop can call is itself authorized for the current
context — the agent doesn't get elevated privileges just because it's "the
agent" (`agentic-ai.ai-security`). Irreversible tool actions require a
human-in-the-loop checkpoint (`agentic-ai.human-in-the-loop`).

## Testing Requirements
Evaluation cases (`agentic-ai.evaluation`) covering: a task solvable in one
tool call, a task requiring multiple sequential tool calls, a task that
should hit the step/cost bound and terminate gracefully, and an adversarial
input attempting to redirect the agent via tool-output injection.

## Common Mistakes
- No step/cost bound, so a confused agent loops until it exhausts budget or
  the request times out ungracefully.
- Feeding raw, unbounded tool output back into context every iteration,
  blowing the context window on a few steps (`agentic-ai.context-engineering`).
- Assuming a framework's default loop implementation already handles
  security/cost bounds correctly without verifying it against this
  project's actual requirements.

## Anti-Patterns
- **Unbounded autonomy**: an agent loop with no step limit "because it
  should just keep going until it's done" — done is not guaranteed to ever
  happen.
- **Framework-first design**: adopting a multi-agent framework's full
  abstraction before validating the single-agent loop actually solves the
  problem simply.

## Validation Checklist
- [ ] Step count, cost, and wall-clock time are all bounded.
- [ ] Bound-exceeded has a defined, graceful fallback.
- [ ] Every step is logged for observability/evaluation.
- [ ] Tool output is treated as untrusted data, not a new instruction.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; an
evaluation harness covers at least one multi-step case and one bound-
exceeded case.

## Example
```csharp
public sealed class AgentLoop(IChatClient model, IToolRegistry tools, ILogger<AgentLoop> logger)
{
    private const int MaxSteps = 10;

    public async Task<AgentResult> RunAsync(string task, CancellationToken ct)
    {
        var messages = new List<ChatMessage> { new(ChatRole.User, task) };

        for (var step = 0; step < MaxSteps; step++)
        {
            ct.ThrowIfCancellationRequested();
            var response = await model.GetResponseAsync(messages, tools.Definitions, ct);
            logger.LogInformation("Step {Step}: {Response}", step, response.Kind);

            if (response.Kind == ChatResponseKind.FinalAnswer)
                return AgentResult.Success(response.Text!);

            foreach (var call in response.ToolCalls)
            {
                var result = await tools.ExecuteAsync(call, ct); // untrusted output
                messages.Add(ChatMessage.ToolResult(call.Id, result.SafeForModelConsumption()));
            }
        }

        return AgentResult.BoundExceeded(step: MaxSteps);
    }
}
```

## Related Skills
- `agentic-ai.tool-calling` — how individual tool calls are defined/executed.
- `agentic-ai.context-engineering` — what goes into the context each step.
- `agentic-ai.fundamentals.planning` — more deliberate multi-step planning
  vs. this reactive loop shape.
- `agentic-ai.reliability` — retry/failure handling within the loop.
