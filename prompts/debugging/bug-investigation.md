---
id: prompt.debugging.bug-investigation
title: Bug Investigation
category: prompt
domain: both
related_skills: []
related_agents: [agent.dotnet-developer]
tags: [debugging]
---

# Bug Investigation

## Purpose
Find and fix a root cause systematically, distinguishing observed fact
from hypothesis — the direct invocation of `workflows/bug-fix.md`.

## When to Use
Any bug report or "this isn't working as expected" request.

## Required Context
The symptom as reported, and reproduction steps or logs if available.

## Prompt

```text
Investigate and fix: [SYMPTOM], following workflows/bug-fix.md.

1. Restate the symptom precisely (expected vs. actual).
2. Attempt to reproduce it; state explicitly if you cannot.
3. Collect evidence (logs, code, data) — label each item as an observed
   fact.
4. Form hypotheses, labeled explicitly as hypotheses, not facts.
5. Test each hypothesis against the actual code/data until the root cause
   is confirmed by evidence — do not fix based on an unconfirmed
   hypothesis.
6. Implement the smallest fix addressing the confirmed root cause.
7. Add a regression test that fails before the fix and passes after.

If the investigation is inconclusive after reasonable effort, say so and
ask for more information rather than guessing at a fix.
```

## Expected Output
A confirmed root cause (with the evidence that confirmed it), a targeted
fix, and a regression test — or an explicit statement that more
information is needed.

## Related Skills / Agents
`agent.dotnet-developer` executes; `agent.test-engineer` for the
regression test if non-trivial.
