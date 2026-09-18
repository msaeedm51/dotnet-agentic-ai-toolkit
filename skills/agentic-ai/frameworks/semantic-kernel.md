---
id: agentic-ai.frameworks.semantic-kernel
title: Semantic Kernel (Optional Framework)
category: skill
domain: agentic-ai
technologies: [dotnet, semantic-kernel]
triggers: [semantic kernel, sk plugin, kernel function]
requires: [agentic-ai.fundamentals.agent-loops, agentic-ai.tool-calling]
related: [agentic-ai.frameworks.microsoft-agent-framework]
optional: []
prerequisites: [agentic-ai.fundamentals.agent-loops]
tags: [semantic-kernel, framework]
---

# Semantic Kernel (Optional Framework)

## Purpose
Implement the concept-first patterns in `skills/agentic-ai/fundamentals/`
using Microsoft's Semantic Kernel SDK — only load this skill when the
project's `.ai/config.yaml` → `ai.frameworks` names `semantic-kernel`.

## When to Use
The project has explicitly chosen Semantic Kernel (existing codebase
convention, or a specific need for its plugin/planner ecosystem). Never the
default starting point — implement against the provider API directly per
`agentic-ai.fundamentals.agent-loops` first, and adopt this only if it
reduces real boilerplate for the project's actual needs.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`, `agentic-ai.tool-calling` — this
skill maps those concepts onto SK's terminology, it doesn't replace
understanding them.

## Inputs Required
Confirmation the project's config actually names this framework — never
introduce it unilaterally.

## Engineering Principles
1. SK "plugins" (functions exposed to the kernel) follow the same design
   discipline as `agentic-ai.tool-calling` — precise schema, wraps an
   already-authorized operation, minimal safe result.
2. SK's planner/agent abstractions still need the same bounds
   (`agentic-ai.fundamentals.agent-loops`), guardrails
   (`agentic-ai.guardrails`), and human-in-the-loop checkpoints
   (`agentic-ai.human-in-the-loop`) as a hand-rolled loop — the framework
   doesn't provide these for free.
3. Keep application code depending on this toolkit's own abstractions
   (`IChatClient`/`IAgentTool` equivalents) where feasible, with SK behind
   the implementation, so a future framework change doesn't ripple through
   every caller.

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` → `ai.frameworks` includes `semantic-kernel`.
2. Register kernel functions wrapping existing, authorized application
   operations — same as any tool in `agentic-ai.tool-calling`.
3. Configure the kernel's model connector(s) per the project's chosen
   provider(s) (`agentic-ai.frameworks.openai`/`.anthropic`/
   `.azure-openai`).
4. Apply this toolkit's bounds/guardrails/evaluation around SK's
   planner/agent execution — don't assume the framework enforces them.

## Code Standards
Kernel function definitions live alongside other tool definitions,
following the same naming/documentation discipline as
`agentic-ai.tool-calling`.

## Architecture Constraints
SK-specific types stay in the agentic-AI implementation layer — Application/
Domain code shouldn't reference SK types directly, same boundary discipline
as any other infrastructure dependency.

## Security Considerations
Same as `agentic-ai.tool-calling` and `agentic-ai.ai-security` — SK doesn't
change the authorization/trust-boundary requirements.

## Testing Requirements
Same as `agentic-ai.evaluation` — SK-based agents get the same evaluation
suite discipline as a hand-rolled implementation.

## Common Mistakes
Assuming SK's built-in planner handles bounds/safety automatically —
verify and add the project's own guardrails explicitly.

## Anti-Patterns
Adopting Semantic Kernel as the default starting point instead of a
deliberate choice verified against `.ai/config.yaml`.

## Validation Checklist
- [ ] `.ai/config.yaml` explicitly names this framework.
- [ ] Kernel functions follow `agentic-ai.tool-calling` discipline.
- [ ] Bounds/guardrails/evaluation are explicitly applied, not assumed.

## Definition of Done
Meets `rules/definition-of-done.md` and the checklists of every core
agentic-ai skill this implementation touches.

## Related Skills
- `agentic-ai.fundamentals.agent-loops` — the concept this implements.
- `agentic-ai.frameworks.microsoft-agent-framework` — an alternative
  Microsoft framework option.
