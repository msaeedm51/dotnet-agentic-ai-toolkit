---
id: prompt.architecture.architecture-analysis
title: Architecture Analysis
category: prompt
domain: both
related_skills: [dotnet.architecture.clean-architecture, dotnet.architecture.ddd]
related_agents: [agent.architect]
tags: [architecture, analysis]
---

# Architecture Analysis

## Purpose
Get a structured evaluation of a proposed or existing architecture's
trade-offs before committing to it, instead of an unstructured opinion.

## When to Use
Evaluating whether to introduce a new pattern, comparing two architectural
approaches, or auditing an existing system's architecture against its
actual requirements.

## Required Context
The requirement(s) driving the decision, and — for an existing-system
audit — the actual codebase (or `workflows/project-discovery.md` output).

## Prompt

```
Analyze the architecture of [SYSTEM/PROPOSAL]. Follow
workflows/architecture-decision.md.

1. State the concrete requirement(s) that make this decision necessary.
2. Identify the simplest approach that could satisfy the requirement, even
   if you expect to reject it.
3. Identify 1-2 additional candidate approaches.
4. For each candidate, evaluate: architectural fit, security implications,
   performance/scalability implications, data implications, and
   implementation/maintenance cost.
5. Recommend one, stating explicitly what was rejected and why.
6. Flag any risk that the recommendation introduces.

Do not recommend a more complex approach than the requirement justifies
(rules/architecture.md). If information needed to decide is missing, say
so instead of assuming.
```

## Expected Output
A structured comparison (not just a recommendation) covering each
candidate's trade-offs, ending in one recommendation with explicit
reasoning and stated risks — ready to become an ADR via
`workflows/architecture-decision.md` stage 7.

## Related Skills / Agents
Loads `dotnet.architecture.*` skills relevant to the candidates being
compared; typically executed by `agent.architect`.
