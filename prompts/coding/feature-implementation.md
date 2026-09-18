---
id: prompt.coding.feature-implementation
title: Feature Implementation
category: prompt
domain: dotnet
related_skills: [dotnet.csharp, dotnet.dotnet]
related_agents: [agent.dotnet-developer, agent.architect]
tags: [implementation, feature]
---

# Feature Implementation

## Purpose
Drive a feature request through the full `workflows/new-feature.md`
sequence instead of jumping straight to code.

## When to Use
Any request to add or change functionality in a .NET (non-agentic-AI)
project.

## Required Context
The requirement, and either an already-produced Project Understanding or
filesystem access to produce one.

## Prompt

```text
Implement: [REQUIREMENT].

Follow workflows/new-feature.md:
1. Restate the requirement; identify and either resolve or flag any
   ambiguity materially affecting architecture or correctness
   (AGENTS.md §7).
2. Inspect existing code for patterns/abstractions to reuse
   (rules/general.md).
3. Identify the architecture boundary this touches and design the
   smallest change that satisfies the requirement.
4. Implement, following rules/csharp.md and rules/dotnet.md and whichever
   skill files apply (resolve via index/skills.yaml).
5. Add tests for the new/changed behavior (rules/testing.md), including
   failure and authorization paths.
6. Note any security- or performance-relevant surface for review.
7. Confirm the change against rules/definition-of-done.md before reporting
   it complete.

Do not expand scope beyond the requirement. State any assumption
explicitly rather than silently picking one.
```

## Expected Output
A working, tested implementation with a concise summary of what changed,
key decisions made, and what (if anything) remains — per `AGENTS.md`
§1.20.

## Related Skills / Agents
`agent.dotnet-developer` executes; `agent.architect` is pulled in for any
non-trivial design decision; `agent.security-reviewer` /
`agent.code-reviewer` follow per the workflow.
