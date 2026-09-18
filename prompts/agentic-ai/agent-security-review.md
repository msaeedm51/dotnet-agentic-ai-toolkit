---
id: prompt.agentic-ai.agent-security-review
title: Agent Security Review
category: prompt
domain: agentic-ai
related_skills: [agentic-ai.ai-security, agentic-ai.guardrails, agentic-ai.human-in-the-loop]
related_agents: [agent.security-reviewer]
tags: [security, agents, prompt-injection]
---

# Agent Security Review

## Purpose
Review an agentic-AI feature specifically for prompt injection, tool-trust,
and privilege-escalation risk — the agentic-AI specialization of
`prompts/security/security-review.md`.

## When to Use
Any agent, tool-calling, or RAG feature before it ships or after a
significant change to its context/tool design.

## Required Context
The agent's tool set, what content enters its context (user input, tool
output, retrieved documents, other agents' output), and what irreversible
actions it can take.

## Prompt

```text
Review [AGENT/FEATURE] for AI-specific security risk, following
agentic-ai.ai-security and rules/agentic-ai.md.

1. Map every point untrusted content enters the model's context.
2. For each, confirm it's structurally distinguished from instructions in
   context assembly, and confirm no tool call can be triggered by text
   parsed from that content rather than the model's structured tool-call
   mechanism.
3. Confirm every tool's authorization matches (never exceeds) the acting
   user's actual permissions.
4. Confirm every irreversible tool action has a human-in-the-loop
   checkpoint enforced in code.
5. Confirm model provider credentials follow standard secret handling.
6. Confirm the evaluation suite includes adversarial cases for each entry
   point identified in step 1.

State each finding as a concrete exploit scenario: what content, through
what entry point, causing what unauthorized effect.
```

## Expected Output
A findings list with concrete prompt-injection/privilege-escalation
scenarios, ranked by severity per `workflows/code-review.md`'s scale.

## Related Skills / Agents
`agent.security-reviewer` executes; a BLOCKER finding blocks merge.
