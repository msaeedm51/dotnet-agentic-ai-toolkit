<!--
Canonical workflow template. A workflow is an ordered, multi-step process,
optionally spanning multiple agents. Do not jump straight from requirement
to implementation — workflows exist to enforce that.
-->
---
id: workflow.<workflow-name>
title: <Workflow Name>
category: workflow
triggers: []
agents_involved: []
skills_loaded: []
tags: []
---

# <Workflow Name>

## Purpose
What situation this workflow governs, and what it prevents (e.g. skipping
straight to code, missing a security pass, shipping an untested migration).

## When to Use
Concrete request shapes that should invoke this workflow — should closely
match `triggers`.

## Participants
Table: step → responsible agent (from `agents_involved`) → what they consume
→ what they produce → who/what consumes it next.

## Stages

### 1. <Stage name>
- **Input:** what must exist before this stage starts.
- **Actions:** what happens.
- **Output:** what this stage produces, handed to the next stage.
- **Gate:** what must be true to proceed (a check, a confirmation, a passing
  test) — or "none" if the stage can't fail.

<!-- Repeat per stage. Typical stage count: 6-12. Do not compress distinct
     concerns (e.g. "security review" and "code review") into one stage. -->

## Escalation
When a stage's gate fails, what happens — retry, hand back to a prior stage,
or escalate to the user per `AGENTS.md` §7.

## Related Workflows
Other `workflows/*.md` this one commonly precedes, follows, or is confused
with (and how to tell them apart).
