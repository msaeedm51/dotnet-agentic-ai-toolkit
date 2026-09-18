---
id: prompt.coding.api-design
title: API Design
category: prompt
domain: dotnet
related_skills: [dotnet.api-design, dotnet.aspnetcore]
related_agents: [agent.api-engineer]
tags: [api, design]
---

# API Design

## Purpose
Decide an API contract deliberately — status codes, DTOs, versioning,
authorization — before implementing the endpoint.

## When to Use
Designing a new endpoint/resource or a new API surface.

## Required Context
The resource(s) and operations needed, and the existing API's conventions
(pagination, versioning, error shape) if one already exists.

## Prompt

```
Design the API for: [REQUIREMENT], following workflows/api-development.md
and dotnet.api-design.

1. Model the resource(s) and operations as HTTP methods on them.
2. Decide the status code for every outcome (success and each failure
   mode).
3. Define request/response DTOs, distinct from domain entities.
4. Decide pagination/filtering/versioning consistent with the existing API
   — or propose a convention if none exists yet.
5. Decide the authorization policy for each operation explicitly.
6. Identify whether this is a breaking change to an existing contract; if
   so, propose a versioning/migration approach.

Do not expose a domain entity directly. Do not leave any outcome's status
code undecided.
```

## Expected Output
A concrete contract: resource routes, DTOs, status codes per outcome, and
an authorization policy per operation — ready for `agent.api-engineer` to
implement.

## Related Skills / Agents
`agent.api-engineer` executes; `agent.security-reviewer` reviews
authorization design.
