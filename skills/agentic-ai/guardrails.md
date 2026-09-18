---
id: agentic-ai.guardrails
title: Guardrails
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [guardrails, content filtering, output validation, input filtering, safety checks]
requires: []
related: [agentic-ai.ai-security, agentic-ai.evaluation, agentic-ai.human-in-the-loop]
optional: []
prerequisites: []
tags: [guardrails, safety]
---

# Guardrails

## Purpose
Enforce automated, code-level checks on agent input and output —
independent of what the prompt asks the model to do — as defense in depth
against the model getting it wrong, being manipulated, or producing an
output the system shouldn't act on.

## When to Use
Any agent/LLM feature where a wrong or manipulated output has a real
consequence — action-taking agents, anything user-facing, anything
touching sensitive data or irreversible operations.

## Prerequisites
None.

## Inputs Required
What specifically must never happen (a concrete list: never call this tool
without X, never output PII in a response meant for another user, never
exceed this cost) — guardrails enforce concrete rules, not vague safety
sentiment.

## Engineering Principles
1. A guardrail is a deterministic, code-level check — not another prompt
   instruction hoping the model complies (`agentic-ai.prompt-engineering`
   — prompts are not a security boundary).
2. Input guardrails validate/filter what enters the model (reject or flag
   suspicious input before it reaches the model, e.g. an obvious prompt-
   injection pattern, though this is defense in depth, not the only
   control).
3. Output guardrails validate what the model produces before it's acted on
   or shown to a user — schema validation, business-rule checks, a
   moderation/safety classifier for user-facing content, PII detection
   before display/storage.
4. Guardrails fail closed — if a check can't be evaluated (e.g. a
   classifier call times out), the default is to block/escalate, not to
   silently allow.
5. Guardrails complement, not replace, tool-level authorization
   (`agentic-ai.tool-calling`) and human-in-the-loop
   (`agentic-ai.human-in-the-loop`) — they're one more layer, not the only
   one.

## Step-by-Step Workflow
1. Enumerate the concrete failure modes this feature must never produce
   (data leak, unauthorized action, harmful/inappropriate content, cost
   blowout).
2. For each, implement a deterministic check: schema/business-rule
   validation for structured output, a classifier or rule-based filter for
   free-text content, a hard limit check for cost/steps.
3. Apply input guardrails before the model call where relevant; apply
   output guardrails before the result is acted on or shown.
4. Define the fail-closed behavior for each guardrail: block and return a
   safe fallback, or escalate to human review.
5. Add evaluation cases (`agentic-ai.evaluation`) specifically targeting
   each guardrail — prove it actually triggers on the input it's meant to
   catch.

## Code Standards
Guardrail checks are named, testable functions/classes with a clear single
responsibility — not scattered inline conditionals mixed into the agent
loop's control flow.

## Architecture Constraints
Guardrails run in code the agent loop always executes — never something the
model can be prompted to skip. They sit at a boundary (before model call,
before tool execution, before output delivery), not buried optionally deep
in a code path that might not always run.

## Security Considerations
Guardrails are part of the defense-in-depth strategy alongside
`agentic-ai.ai-security` (prompt injection, tool-output trust) and
`agentic-ai.tool-calling` (authorization) — don't treat a guardrail as
sufficient on its own if the underlying operation isn't also independently
authorized.

## Testing Requirements
Every guardrail has an evaluation case proving it triggers on the input
it's designed to catch, and doesn't false-positive on legitimate input
often enough to be disruptive.

## Common Mistakes
- Implementing a guardrail as a prompt instruction instead of a code-level
  check, making it bypassable by a sufficiently adversarial or just
  unlucky input.
- Failing open (allowing the action) when a guardrail check itself errors
  out, instead of failing closed.
- No guardrail for cost/step blowout, relying only on the agent loop's own
  bound (`agentic-ai.fundamentals.agent-loops`) with no independent check.

## Anti-Patterns
- **Guardrail theater**: a check that logs a warning but doesn't actually
  block anything, giving false confidence.
- **Single point of trust**: relying on one guardrail (e.g. output
  validation) as the only defense, with no input-side or tool-authorization
  checks backing it up.

## Validation Checklist
- [ ] Every concrete failure mode has a deterministic, code-level check.
- [ ] Guardrails fail closed on error, not open.
- [ ] Guardrails run unconditionally in the code path, not optionally.
- [ ] Each guardrail has an evaluation case proving it triggers correctly.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; each
guardrail's trigger and fail-closed behavior are covered by tests.

## Example
```csharp
public sealed class OutputGuardrails(IPiiDetector piiDetector)
{
    public async Task<GuardrailResult> CheckAsync(string modelOutput, AgentContext ctx, CancellationToken ct)
    {
        GuardrailResult piiCheck;
        try
        {
            piiCheck = await piiDetector.CheckAsync(modelOutput, ct);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            return GuardrailResult.Block("PII check failed; failing closed."); // fail closed, not open
        }

        return piiCheck.ContainsPii && !ctx.RecipientIsDataOwner
            ? GuardrailResult.Block("Output contains PII not belonging to the recipient.")
            : GuardrailResult.Allow();
    }
}
```

## Related Skills
- `agentic-ai.ai-security` — the broader trust-boundary discipline
  guardrails are one layer of.
- `agentic-ai.evaluation` — proving each guardrail actually works.
- `agentic-ai.human-in-the-loop` — the escalation path when a guardrail
  blocks.
