---
id: agentic-ai.reliability
title: Reliability
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [llm call reliability, retry model call, provider outage, fallback model, timeout llm]
requires: [dotnet.dotnet]
related: [agentic-ai.fundamentals.agent-loops, agentic-ai.observability, agentic-ai.model-routing]
optional: []
prerequisites: []
tags: [reliability, resilience, agents]
---

# Reliability

## Purpose
Handle model provider failures, timeouts, and rate limits gracefully —
applying the same resilience discipline as any external dependency
(`dotnet.dotnet`), plus the agent-loop-specific failure modes (a stuck
loop, a partially-completed multi-step task).

## When to Use
Any production call to an LLM provider or agent loop — provider outages,
rate limits, and timeouts are not edge cases at real scale, they're routine.

## Prerequisites
`dotnet.dotnet` for `HttpClientFactory`/resilience fundamentals.

## Inputs Required
The provider's documented rate limits and typical latency, and what a
graceful degradation looks like for this specific feature (a cached/
fallback response, a simpler model, or an explicit "try again" to the
user).

## Engineering Principles
1. Every model provider call goes through the same resilience pattern as
   any external HTTP dependency: timeout, retry with backoff (respecting
   the provider's rate-limit signals), circuit breaker
   (`dotnet.dotnet`).
2. Retries must account for cost — blindly retrying an expensive call
   multiple times multiplies cost; cap retries and prefer a cheaper
   fallback over repeated retries of the same expensive call where
   possible.
3. A partially-completed agent loop (crashed/timed-out mid-run) needs a
   defined recovery behavior — resume, restart cleanly, or fail visibly —
   never silently lost with no trace.
4. Define a fallback for provider unavailability: a secondary provider/
   model (`agentic-ai.model-routing`), a cached previous response if
   applicable, or a clear "unavailable, try again" — never a silent hang.
5. Idempotency matters for agent actions that might be retried after a
   timeout whose actual outcome is unknown (did the tool call complete
   before the timeout, or not?) — design tools to be safely retryable
   (`agentic-ai.tool-calling`).

## Step-by-Step Workflow
1. Wrap every model provider call with a timeout, retry-with-backoff
   (respecting `Retry-After` headers where provided), and circuit breaker.
2. Define the fallback behavior when the circuit is open or retries are
   exhausted: a fallback model/provider, a cached response, or an explicit
   failure the caller can act on.
3. For agent loops, persist enough state to recover or resume after a
   crash/timeout — or at minimum, ensure a partial failure produces a clear
   log entry and a bounded, safe result rather than an indefinite hang.
4. Design tool calls to be idempotent where they might be retried after an
   ambiguous timeout (did it actually execute?).
5. Monitor provider error rates and latency (`agentic-ai.observability`) to
   detect degradation before it becomes a full outage-driven incident.

## Code Standards
Model provider calls go through a typed client with `HttpClientFactory` +
resilience policy, same as any other external dependency
(`dotnet.dotnet`) — never a bare, unwrapped SDK call on the critical path.

## Architecture Constraints
Fallback/degradation behavior is defined per feature, not globally
assumed — a chat feature might degrade to "try again," while a
safety-critical classification might need to fail closed (block, don't
guess) rather than degrade to a lower-quality answer.

## Security Considerations
A fallback to a secondary provider must meet the same data-handling
requirements as the primary — don't silently fall back to a provider that
doesn't meet the project's compliance requirements just because it's
available.

## Testing Requirements
Test the resilience policy directly: a simulated timeout triggers the
retry/fallback path, a simulated persistent failure opens the circuit
breaker and returns the defined fallback, not an unhandled exception.

## Common Mistakes
- No timeout on a model provider call, letting a hung request block a
  request thread/agent step indefinitely.
- Retrying an expensive call many times without a cost-aware cap, multiplying
  spend during a provider degradation instead of failing fast.
- No idempotency on a tool action that gets retried after an ambiguous
  timeout, causing a duplicate side effect (e.g. sending the same email
  twice).

## Anti-Patterns
- **Unbounded retry loop**: retrying indefinitely on failure with no cap,
  compounding cost and latency during an outage instead of failing fast to
  a defined fallback.
- **Silent partial failure**: an agent loop that crashes mid-run with no
  log entry or recoverable state, leaving no trace of what happened.

## Validation Checklist
- [ ] Every provider call has a timeout, bounded retry, and circuit
      breaker.
- [ ] A defined fallback exists for provider unavailability.
- [ ] Retryable tool actions are idempotent.
- [ ] Agent loop failures are logged with enough state to diagnose or
      resume.

## Definition of Done
Meets `rules/definition-of-done.md`; resilience policy is tested against
simulated timeout and persistent-failure scenarios.

## Example
```csharp
builder.Services.AddHttpClient<IChatClient, OpenAiChatClient>(c =>
        c.Timeout = TimeSpan.FromSeconds(30))
    .AddResilienceHandler("llm-provider", pipeline =>
    {
        pipeline.AddRetry(new HttpRetryStrategyOptions
        {
            MaxRetryAttempts = 2, // cost-aware: not unbounded
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = args => ValueTask.FromResult(args.Outcome.Result?.StatusCode == HttpStatusCode.TooManyRequests)
        });
        pipeline.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions());
    });
```

## Related Skills
- `agentic-ai.fundamentals.agent-loops` — where recovery/resumption matters
  most.
- `agentic-ai.model-routing` — fallback to an alternative model/provider.
- `agentic-ai.observability` — detecting degradation before full outage.
