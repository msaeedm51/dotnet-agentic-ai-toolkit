---
id: agentic-ai.frameworks.microsoft-agent-framework
title: Microsoft Agent Framework (Optional Framework)
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [microsoft agent framework, ms agent framework]
requires: [agentic-ai.fundamentals.agent-loops, agentic-ai.fundamentals.multi-agent-systems]
related: [agentic-ai.frameworks.semantic-kernel]
optional: []
prerequisites: [agentic-ai.fundamentals.multi-agent-systems]
tags: [microsoft-agent-framework, framework]
---

# Microsoft Agent Framework (Optional Framework)

## Purpose
Implement the concept-first patterns in `skills/agentic-ai/fundamentals/`
(especially multi-agent orchestration) using Microsoft's Agent Framework —
only load this skill when `.ai/config.yaml` → `ai.frameworks` names it.

## When to Use
The project has explicitly chosen this framework, typically for its
multi-agent orchestration support. Never the default — validate the
concept-first design (`agentic-ai.fundamentals.multi-agent-systems`) first.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`,
`agentic-ai.fundamentals.multi-agent-systems`.

## Inputs Required
Confirmation the project's config names this framework.

## Engineering Principles
1. Agents defined in this framework still need this toolkit's bounds
   (per-agent and aggregate, `agentic-ai.fundamentals.multi-agent-systems`),
   guardrails, and human-in-the-loop checkpoints applied explicitly.
2. Orchestration/handoff patterns follow the same structured-handoff
   discipline as `agentic-ai.fundamentals.multi-agent-systems` — minimal,
   structured context per handoff, not a full history dump.
3. Keep application/domain code independent of this framework's types —
   it's an implementation detail of the agentic-AI layer.

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` → `ai.frameworks` includes this framework.
2. Define each specialist agent's scope/tools narrowly, per
   `agentic-ai.fundamentals.multi-agent-systems`.
3. Configure orchestration (supervisor/routing pattern by default) with
   explicit aggregate bounds.
4. Apply this toolkit's guardrails, evaluation, and observability around
   the framework's execution — don't assume they're provided by default.

## Code Standards
Same as `agentic-ai.tool-calling`/`agentic-ai.fundamentals.multi-agent-systems`
for tool and agent definitions built on this framework.

## Architecture Constraints
Framework types stay in the agentic-AI implementation layer.

## Security Considerations
Same as `agentic-ai.ai-security` — no framework-specific relaxation of
tool authorization or trust-boundary rules.

## Testing Requirements
Same as `agentic-ai.evaluation`, including routing-correctness cases for
the multi-agent orchestration.

## Common Mistakes
Assuming the framework's orchestration primitives enforce cost/step bounds
by default — verify and add the project's own aggregate bound.

## Anti-Patterns
Adopting a multi-agent framework before establishing (per
`agentic-ai.fundamentals.multi-agent-systems`) that a single agent
genuinely can't serve the task.

## Validation Checklist
- [ ] `.ai/config.yaml` explicitly names this framework.
- [ ] Aggregate bounds and guardrails are explicitly configured.
- [ ] Handoffs use structured, minimal context.

## Definition of Done
Meets `rules/definition-of-done.md` and the checklists of every core
agentic-ai skill this implementation touches.

## Related Skills
- `agentic-ai.fundamentals.multi-agent-systems` — the concept this
  implements.
- `agentic-ai.frameworks.semantic-kernel` — an alternative Microsoft
  framework option, more focused on single-agent plugin composition.
