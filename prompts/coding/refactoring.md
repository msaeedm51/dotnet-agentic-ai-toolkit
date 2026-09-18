---
id: prompt.coding.refactoring
title: Refactoring
category: prompt
domain: dotnet
related_skills: [dotnet.csharp]
related_agents: [agent.dotnet-developer, agent.test-engineer]
tags: [refactoring]
---

# Refactoring

## Purpose
Restructure code safely, with a verified safety net, instead of a rewrite
that risks silently changing behavior.

## When to Use
A request to clean up, restructure, or improve existing code with no
intended behavior change.

## Required Context
The target code and its current test coverage.

## Prompt

```text
Refactor [TARGET], following workflows/refactoring.md:

1. Identify current behavior and every caller of this code.
2. Assess existing test coverage; if it's insufficient to catch an
   accidental behavior change, add characterization tests first.
3. Refactor in small, independently verifiable increments.
4. Run tests after each increment — do not proceed to the next increment
   on a failure.
5. Confirm the final diff contains no behavior change and no unrelated
   changes (rules/general.md).

If you discover the "refactor" actually requires a behavior change, stop
and say so explicitly rather than silently expanding scope — that's a
different workflow (workflows/new-feature.md).
```

## Expected Output
An incremental diff with passing tests at every step, and confirmation
that observable behavior is unchanged.

## Related Skills / Agents
`agent.dotnet-developer` executes; `agent.test-engineer` for
characterization test design when coverage is insufficient.
