---
id: agentic-ai.prompt-engineering
title: Prompt Engineering
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [system prompt, prompt design, few shot examples, prompt versioning]
requires: []
related: [agentic-ai.context-engineering, agentic-ai.evaluation, agentic-ai.structured-outputs]
optional: []
prerequisites: []
tags: [agents, prompting]
---

# Prompt Engineering

## Purpose
Design prompts (system instructions, few-shot examples, task framing) that
produce reliable behavior — treated as a versioned, tested engineering
artifact, not a string tweaked ad hoc until it "seems to work."

## When to Use
Any time model behavior is driven by a prompt this codebase owns and
controls — system prompts, task templates, few-shot examples.

## Prerequisites
None.

## Inputs Required
The specific behavior the prompt needs to produce, and what "good" output
looks like concretely enough to write an evaluation case for it.

## Engineering Principles
1. A prompt is versioned code, not a runtime-editable string with no
   history — a prompt change is a change to system behavior and gets the
   same review/testing rigor as any other behavior change.
2. Be specific and concrete — vague instructions ("be helpful") produce
   inconsistent behavior; explicit constraints, format requirements, and
   examples produce reliable behavior.
3. Few-shot examples should cover the actual distribution of real inputs,
   including edge cases, not just one clean happy-path example.
4. Separate stable instructions (system prompt: role, constraints, output
   format) from per-request variable content (the actual task/user input)
   — don't rebuild the whole instruction set per request.
5. A prompt change is evaluated against the same evaluation suite
   (`agentic-ai.evaluation`) before and after, to catch regressions a
   "it reads better to me" judgment would miss.

## Step-by-Step Workflow
1. Write the initial prompt with a specific, concrete task description,
   explicit constraints (what NOT to do matters as much as what to do),
   and the exact output format expected.
2. Add few-shot examples covering the realistic range of inputs, including
   at least one edge case and one example of the correct refusal/fallback
   behavior if applicable.
3. Store the prompt as versioned source (a file or a typed constant), not a
   value editable at runtime with no audit trail.
4. Run it against the evaluation suite (`agentic-ai.evaluation`); iterate
   based on actual failures, not intuition.
5. Before changing an existing prompt in production use, run the same
   evaluation suite against the new version and compare — a prompt change
   is a behavior change and needs the same regression discipline.

## Code Standards
Prompts live in source-controlled files/constants with a clear name and,
ideally, a version identifier — never string-built ad hoc inline at every
call site with duplicated instructions.

## Architecture Constraints
Prompt templates are a distinct artifact from the code that calls the
model — separable so they can be evaluated, diffed, and versioned
independently of the calling logic.

## Security Considerations
A system prompt is not a security boundary — instructions like "never
reveal the system prompt" or "never do X" are a behavioral nudge, not
enforcement; the actual enforcement is code-level (tool authorization,
guardrail checks, output filtering) — see `agentic-ai.ai-security` and
`agentic-ai.guardrails`. Don't rely on prompt wording alone to prevent a
consequential action.

## Testing Requirements
Every prompt used in production has an evaluation suite covering its
intended behavior and known failure modes (`agentic-ai.evaluation`); a
prompt change requires re-running that suite before shipping.

## Common Mistakes
- Editing a production prompt directly with no version history and no
  before/after evaluation, making regressions invisible until a user
  reports one.
- Vague instructions that work on the examples tried manually but fail on
  the actual distribution of real inputs.
- Relying on the system prompt alone to prevent a security-relevant
  behavior instead of enforcing it in code.

## Anti-Patterns
- **Prompt spaghetti**: instructions accreted over time with contradictory
  or redundant guidance, never cleaned up, making behavior unpredictable.
- **Prompt-as-security**: trusting "don't do X" phrasing in the prompt as
  the actual control preventing X, instead of a code-level guardrail.

## Validation Checklist
- [ ] Prompt is versioned, source-controlled content, not an ad hoc string.
- [ ] Few-shot examples cover realistic input variety, including edge
      cases.
- [ ] An evaluation suite exists and is re-run on every prompt change.
- [ ] No security-relevant behavior relies on prompt wording alone.

## Definition of Done
Meets `rules/definition-of-done.md`; a prompt change is accompanied by an
evaluation run showing no regression against the existing suite.

## Example
```csharp
public static class SupportAgentPrompts
{
    public const string Version = "2024-06-v3";

    public const string System = """
        You are a customer support triage assistant. Classify the ticket into
        exactly one category: Billing, Technical, AccountAccess, or Other.
        If the ticket contains a request you cannot help with (e.g. a refund
        approval), classify it and note that a human must handle the action —
        do not attempt to perform it yourself.
        Respond only in the provided JSON schema.
        """;
}
```

## Related Skills
- `agentic-ai.context-engineering` — how the rest of the context around
  this prompt is assembled.
- `agentic-ai.evaluation` — the test suite a prompt change is measured
  against.
- `agentic-ai.structured-outputs` — the output-format half of prompt
  design.
