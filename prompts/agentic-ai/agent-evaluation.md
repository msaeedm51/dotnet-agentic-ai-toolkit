---
id: prompt.agentic-ai.agent-evaluation
title: Agent Evaluation Suite Generation
category: prompt
domain: agentic-ai
related_skills: [agentic-ai.evaluation]
related_agents: [agent.test-engineer, agent.ai-engineer]
tags: [evaluation, testing, agents]
---

# Agent Evaluation Suite Generation

## Purpose
Build or extend an evaluation suite for agent/LLM behavior — the
agentic-AI equivalent of `prompts/testing/test-generation.md`.

## When to Use
A new agent/prompt/RAG pipeline needs an evaluation suite, or an existing
one needs cases added for a newly discovered failure mode.

## Required Context
The agent/feature's intended behavior, known constraints (what it must
never do), and any production issue that motivated adding a new case.

## Prompt

```
Build an evaluation suite for [AGENT/FEATURE], following
agentic-ai.evaluation.

1. Write cases covering the realistic input distribution: clear
   happy-path requests, ambiguous requests, and out-of-scope requests.
2. Write at least one adversarial case per untrusted-content entry point
   (a prompt-injection attempt via tool output, retrieved content, or user
   input trying to override stated constraints).
3. For each case, define how it's scored: exact/schema match where
   possible, a rule-based check, or LLM-as-judge only where a
   deterministic check genuinely can't capture the criterion.
4. If using LLM-as-judge, note that it needs calibration against human
   judgment before being trusted — do not assume it's accurate.
5. Record a baseline pass rate so future changes can be compared against
   it.

If this evaluation is prompted by a production issue, include that exact
failure as a new case.
```

## Expected Output
A structured, versioned evaluation dataset with scoring defined per case
and a recorded baseline — not ad hoc manual testing.

## Related Skills / Agents
`agent.test-engineer` or `agent.ai-engineer` executes.
