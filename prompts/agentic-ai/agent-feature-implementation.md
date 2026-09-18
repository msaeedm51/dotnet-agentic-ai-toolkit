---
id: prompt.agentic-ai.agent-feature-implementation
title: Agentic AI Feature Implementation
category: prompt
domain: agentic-ai
related_skills: [agentic-ai.fundamentals.agent-loops, agentic-ai.tool-calling]
related_agents: [agent.ai-engineer, agent.architect]
tags: [agentic-ai, implementation]
---

# Agentic AI Feature Implementation

## Purpose
Drive an agentic-AI feature request through the full
`workflows/agentic-ai-feature.md` sequence — pattern selection, bounds,
guardrails, and an evaluation harness, not just "wire up an LLM call."

## When to Use
A request to build or modify an agent, RAG pipeline, tool-calling feature,
or any agentic-AI capability.

## Required Context
The requirement, what the agent should explicitly not do (irreversible
actions in scope), and the project's `.ai/config.yaml`
(`ai.model_providers`, `ai.frameworks`, `ai.patterns`).

## Prompt

```text
Implement: [REQUIREMENT], following workflows/agentic-ai-feature.md.

1. Restate the requirement, including what the agent must NOT do.
2. Check .ai/config.yaml for model provider/framework/pattern
   constraints before choosing an approach.
3. Select the simplest agent pattern that fits (single-agent loop, RAG,
   tool-use, plan-then-execute, or multi-agent) per
   agentic-ai.fundamentals — do not default to the most sophisticated
   pattern.
4. Design bounds (max steps, cost, timeout) and identify every
   irreversible tool action needing a human-in-the-loop checkpoint
   (agentic-ai.human-in-the-loop) before implementing.
5. Implement, with bounds/guardrails enforced in code, not just prompt
   instructions (rules/agentic-ai.md).
6. Build an evaluation suite covering happy-path, edge, and at least one
   adversarial (prompt-injection-style) case.
7. Confirm against rules/definition-of-done.md and rules/agentic-ai.md.

Never let a tool call execute based on text parsed from untrusted
content — only from the model's structured tool-call mechanism.
```

## Expected Output
A working, bounded, evaluated implementation with guardrails enforced in
code, plus a summary of the pattern chosen and why.

## Related Skills / Agents
`agent.ai-engineer` executes; `agent.architect` for pattern selection;
`agent.security-reviewer` and `agent.performance-engineer` follow per the
workflow.
