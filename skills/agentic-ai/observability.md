---
id: agentic-ai.observability
title: Observability (Agentic AI)
category: skill
domain: agentic-ai
technologies: [dotnet, opentelemetry]
triggers: [agent tracing, llm observability, token usage tracking, agent run logging]
requires: [dotnet.dotnet]
related: [agentic-ai.cost-optimization, agentic-ai.reliability, agentic-ai.evaluation]
optional: []
prerequisites: [dotnet.dotnet]
tags: [observability, tracing, agents]
---

# Observability (Agentic AI)

## Purpose
Make agent/LLM behavior debuggable and measurable in production — every
step, tool call, token count, and decision traceable — extending the
project's standard OpenTelemetry setup (`dotnet.dotnet`) with the
agent-specific signals that matter.

## When to Use
Every agentic-AI feature in production. An agent with no observability is
undebuggable the first time it behaves unexpectedly — this isn't optional
polish.

## Prerequisites
`dotnet.dotnet` for the base OpenTelemetry/logging setup.

## Inputs Required
What questions you'll need to answer in production ("why did the agent call
this tool," "how much is this feature costing per day," "which prompt
version produced this response") — instrument for those specifically.

## Engineering Principles
1. One correlation/trace id spans an entire agent run (and, for multi-agent
   systems, the entire handoff chain) — so a production issue can be traced
   end to end, not just per isolated model call.
2. Log every model call's key metadata: prompt version, model/provider
   used, token counts (input/output), latency, and cost — this is the data
   `agentic-ai.cost-optimization` and `agentic-ai.reliability` depend on.
3. Log every tool call: which tool, arguments (redacted if sensitive),
   result summary, success/failure, latency.
4. Log the agent's actual decisions (which step it took and why, if the
   model provides reasoning) at a level useful for debugging without
   logging full untrusted content verbatim where that would leak sensitive
   data.
5. Never log secrets, full PII payloads, or raw model provider API keys —
   same discipline as any other logging (`dotnet.security`).

## Step-by-Step Workflow
1. Generate/propagate one correlation id for the full agent run (and
   handoff chain, if multi-agent) at the entry point.
2. Instrument every model call with an OpenTelemetry span capturing model/
   provider, prompt version, token counts, latency, and cost.
3. Instrument every tool call similarly: tool name, redacted arguments,
   success/failure, latency.
4. Emit structured logs for agent-level decisions (which step, which tool,
   why) at a level that's useful for post-incident debugging.
5. Build a dashboard/alert on the metrics that matter operationally: error
   rate, latency, cost per run, guardrail trigger rate.

## Code Standards
Agent/tool call spans follow the same `ILogger`/OpenTelemetry conventions
as the rest of the codebase (`dotnet.dotnet`) — not a separate, bespoke
logging mechanism just for agentic-AI code.

## Architecture Constraints
Observability instrumentation is added at the agent loop and tool-calling
layer centrally (e.g. via a decorator/middleware around every model/tool
call), not manually duplicated at every individual call site.

## Security Considerations
Logged tool arguments and model prompts/completions must be reviewed for
what they might contain — redact PII, secrets, and full untrusted document
content where full logging isn't necessary for debugging
(`dotnet.security`).

## Testing Requirements
Verify the correlation id actually propagates through a full multi-step/
multi-agent run in an integration test — a broken correlation chain is a
silent observability gap that's easy to introduce and hard to notice until
you need it during an incident.

## Common Mistakes
- No correlation id linking a multi-step agent run together, making a
  production issue nearly impossible to trace end to end.
- Logging full prompts/completions verbatim including PII/secrets, creating
  a compliance problem in the logging pipeline itself.
- Only logging errors, missing the token/cost/latency data needed to
  answer "why did this get expensive" after the fact.

## Anti-Patterns
- **Black-box agent**: no instrumentation at all beyond a top-level
  success/failure log, giving no insight into what actually happened
  during the run.
- **Log-everything with no redaction**: capturing full raw content for
  debugging convenience without considering what sensitive data ends up in
  the logging pipeline.

## Validation Checklist
- [ ] One correlation id spans the full agent run/handoff chain.
- [ ] Every model call logs token counts, latency, cost, and prompt
      version.
- [ ] Every tool call logs name, redacted arguments, and outcome.
- [ ] No secret or full PII payload is logged.

## Definition of Done
Meets `rules/definition-of-done.md`; an integration test confirms
correlation id propagation across a multi-step run.

## Example
```csharp
using var activity = ActivitySource.StartActivity("agent.run", ActivityKind.Internal);
activity?.SetTag("agent.run_id", runId);

using (activity?.SetTag("llm.model", "gpt-4o").SetTag("llm.prompt_version", SupportAgentPrompts.Version) is var _)
{
    var sw = Stopwatch.StartNew();
    var response = await model.GetResponseAsync(messages, ct);
    activity?.SetTag("llm.input_tokens", response.Usage.InputTokens)
             .SetTag("llm.output_tokens", response.Usage.OutputTokens)
             .SetTag("llm.latency_ms", sw.ElapsedMilliseconds)
             .SetTag("llm.cost_usd", response.Usage.EstimatedCostUsd);
}
```

## Related Skills
- `dotnet.dotnet` — the base OpenTelemetry/logging setup this extends.
- `agentic-ai.cost-optimization` — the primary consumer of token/cost
  telemetry.
- `agentic-ai.reliability` — detecting degradation via observability data.
