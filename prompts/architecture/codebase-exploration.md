---
id: prompt.architecture.codebase-exploration
title: Codebase Exploration
category: prompt
domain: both
related_skills: []
related_agents: [agent.architect]
tags: [discovery, exploration]
---

# Codebase Exploration

## Purpose
Produce the "Project Understanding" this toolkit expects before any
substantive change to an unfamiliar project — a direct invocation of
`workflows/project-discovery.md`.

## When to Use
The first task in a project not yet inspected this session, or when asked
to explain how an existing system works before changing it.

## Required Context
Filesystem access to the project (or the user pasting relevant files if
unavailable — `AGENTS.md` §2).

## Prompt

```
Explore this codebase and produce a Project Understanding, following
workflows/project-discovery.md:

1. Solution/project structure and dependency graph.
2. Technology stack actually in use (verify, don't assume from any
   template or typical-project expectation).
3. Data access approach and database engine(s).
4. Authentication/authorization scheme.
5. API surface and the architecture pattern actually followed (not
   necessarily what documentation claims).
6. Testing strategy and what's actually covered.
7. CI/CD, containerization, and deployment model.
8. Existing conventions to follow for any new work.
9. Risks or inconsistencies noticed.

Do not invent a component, dependency, or convention you haven't actually
verified in the code (rules/anti-hallucination.md).
```

## Expected Output
A concise Project Understanding summary usable as the starting context for
any subsequent workflow in this project this session.

## Related Skills / Agents
Feeds every other workflow; typically the first action of `agent.architect`
or whichever agent picks up the task.
