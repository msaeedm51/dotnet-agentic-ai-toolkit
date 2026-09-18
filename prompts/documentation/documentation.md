---
id: prompt.documentation.documentation
title: Documentation Generation
category: prompt
domain: both
related_skills: [dotnet.documentation]
related_agents: [agent.documentation-engineer]
tags: [documentation]
---

# Documentation Generation

## Purpose
Produce documentation scoped to what actually changed and verified
against the current code — not speculative or drifted-from-reality docs.

## When to Use
A change affects setup steps, a public contract, or warrants an ADR; or a
request to document an existing feature/decision.

## Required Context
What changed (or what needs documenting), the intended reader (developer,
operator, external API consumer), and the current code to verify against.

## Prompt

```text
Produce documentation for: [SUBJECT], following dotnet.documentation.

1. Identify the audience and purpose (setup guide, API reference, ADR,
   runbook, feature documentation).
2. Verify current behavior/setup steps against the actual code — do not
   document from memory or assumption.
3. Write for the specific reader's need (a runbook is exact steps; an ADR
   is Status/Context/Decision/Alternatives/Consequences/Risks).
4. Link to related existing documentation instead of duplicating it.
5. Do not include any live secret or production credential.

Only produce documentation actually required by the change — do not
generate speculative documentation for unaffected areas.
```

## Expected Output
Documentation scoped to the actual need, verified against current code,
using the appropriate format for its audience.

## Related Skills / Agents
`agent.documentation-engineer` executes.
