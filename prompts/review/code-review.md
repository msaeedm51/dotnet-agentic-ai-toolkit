---
id: prompt.review.code-review
title: Code Review
category: prompt
domain: both
related_skills: []
related_agents: [agent.code-reviewer]
tags: [review]
---

# Code Review

## Purpose
Produce a structured, severity-ranked review of a diff/PR — the direct
invocation of `workflows/code-review.md`.

## When to Use
A request to review a diff, PR, or specific piece of code.

## Required Context
The diff/PR to review, and the surrounding code's existing conventions.

## Prompt

```
Review [DIFF/PR], following workflows/code-review.md.

Cover: correctness (including edge and failure cases), architecture fit
(rules/architecture.md), maintainability, security (rules/security.md —
escalate anything security-relevant), performance (only flag with actual
evidence, not speculation), test coverage, error handling, and breaking
changes.

For each finding, state: severity (BLOCKER/HIGH/MEDIUM/LOW/INFO), exact
location, the problem, its concrete impact, and a specific recommendation.
Do not produce an arbitrary aggregate score. Do not duplicate findings for
the same root cause.
```

## Expected Output
A findings list in the format above, ranked most-severe first, with no
finding lacking a concrete location and failure scenario.

## Related Skills / Agents
`agent.code-reviewer` executes; `agent.security-reviewer` and
`agent.performance-engineer` contribute findings in their domains per
`workflows/code-review.md`.
