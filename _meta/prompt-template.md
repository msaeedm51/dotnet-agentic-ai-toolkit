<!--
Canonical prompt template. Prompts are thin — they combine a skill + an
agent + (often) a workflow into a ready-to-use request shape. Keep prompt
bodies LLM-agnostic: "AI assistant," not a vendor name. Vendor-specific
phrasing/formatting belongs only in adapters/*.md, which may wrap this
prompt but must not restate its content.
-->
---
id: prompt.<category>.<prompt-name>
title: <Prompt Name>
category: prompt
domain: dotnet | agentic-ai | both
related_skills: []
related_agents: []
tags: []
---

# <Prompt Name>

## Purpose
What this prompt is for and what makes it worth having as a named,
reusable template rather than writing the request ad hoc each time.

## When to Use
Concrete situations this prompt fits.

## Required Context
What the user/AI assistant needs to gather or supply before using this
prompt (files, config, constraints) — be specific enough that the prompt
doesn't silently produce a generic answer for lack of context.

## Prompt

```text
<The actual reusable prompt text, written for "the AI assistant," with
placeholders in ALL_CAPS or <angle-brackets> for the caller to fill in.>
```

## Expected Output
What a good response to this prompt looks like — shape, not full content
(e.g. "an implementation plan with numbered steps and identified risks," not
a worked example).

## Related Skills / Agents
Cross-reference `related_skills` / `related_agents` from frontmatter in
prose — which skill(s) this prompt expects to be loaded, which agent role
typically executes it.
