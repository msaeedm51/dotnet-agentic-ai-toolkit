---
id: prompt.security.security-review
title: Security Review
category: prompt
domain: both
related_skills: [dotnet.security, agentic-ai.ai-security]
related_agents: [agent.security-reviewer]
tags: [security, review]
---

# Security Review

## Purpose
Review a change for concrete, exploitable security risk — with a specific
exploit path, not a generic vulnerability checklist recited without
context.

## When to Use
Any change touching authentication, authorization, input handling, data
exposure, secrets, or — for agentic-AI — prompt/tool trust boundaries.

## Required Context
The diff/design under review, and whether it's `dotnet` track,
`agentic-ai` track, or both.

## Prompt

```text
Perform a security review of [DIFF/DESIGN], following dotnet.security
(and agentic-ai.ai-security + rules/agentic-ai.md if this touches the
agentic-AI track).

Check specifically for: missing/incorrect authorization enforcement,
unparameterized SQL, unencoded output reaching a browser, secrets in code
or logs, unrestricted outbound requests from user input (SSRF), insecure
file upload handling, and — for agentic-AI — untrusted tool/retrieved
content not clearly separated from instructions, missing loop/cost bounds,
and missing human-in-the-loop gates on irreversible actions.

For each finding, state the concrete exploit path: what input, through
what boundary, causing what effect. Assign severity per
workflows/code-review.md's scale.
```

## Expected Output
A findings list with concrete exploit scenarios, ranked by severity, with
no finding that's just a generic "consider security here."

## Related Skills / Agents
`agent.security-reviewer` executes; a BLOCKER finding here blocks merge
per `agents/security-reviewer.md`.
