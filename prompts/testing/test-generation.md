---
id: prompt.testing.test-generation
title: Test Generation
category: prompt
domain: dotnet
related_skills: [dotnet.testing]
related_agents: [agent.test-engineer]
tags: [testing]
---

# Test Generation

## Purpose
Generate test coverage at the right level (unit/integration/API/
architecture) for a specific piece of behavior, including failure and
authorization paths — not just a happy-path test.

## When to Use
A behavior change needs test coverage, or existing coverage needs a gap
filled.

## Required Context
The code/behavior under test, and its dependencies (to determine whether a
unit, integration, or API test is appropriate — `dotnet.testing`).

## Prompt

```text
Write tests for: [TARGET], following dotnet.testing and rules/testing.md.

1. Classify the right test level: unit (pure logic, no I/O), integration
   (real infrastructure boundary via Testcontainers), or API
   (WebApplicationFactory).
2. Cover the success/happy path.
3. Cover every defined failure mode explicitly (validation failure,
   not-found, conflict).
4. Cover the authorization boundary if one exists: both the allowed and
   the denied case.
5. Do not mock a dependency the test is meant to verify the behavior of
   (e.g. don't mock the repository in a test meant to verify a query
   returns correct results).
6. Do not assert on implementation details that aren't part of the
   observable contract.
```

## Expected Output
A test suite for the target, covering success, failure, and authorization
paths, at the appropriate test level, that fails without the target
behavior and passes with it.

## Related Skills / Agents
`agent.test-engineer` executes for non-trivial cases; simple cases can be
handled inline by whichever agent implemented the behavior.
