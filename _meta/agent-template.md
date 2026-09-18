<!--
Canonical agent template. An "agent" here is a role definition consumed by
an AI assistant (directly, or via a platform's subagent/persona feature) —
not a clone per domain. If a role applies to both tracks, make it
domain-aware (see "Skills to Load") instead of creating a second file.
-->
---
id: agent.<agent-name>
title: <Role Name> Agent
category: agent
domains: [dotnet, agentic-ai]   # list only the domains this role actually operates in
skills_default: []
escalates_to: []
tags: []
---

# <Role Name> Agent

## Role
One sentence: what this agent is responsible for that no other agent is.

## Objective
What "success" looks like for this agent on a typical task.

## Responsibilities
Bullet list — concrete, non-overlapping with other agents. If this overlaps
another agent's responsibilities, resolve the overlap here explicitly
("X belongs to the Security Reviewer, not this agent") rather than leaving
ambiguity.

## Inputs
What this agent needs before starting: from the project, from the user, from
another agent's output (name which agent/workflow step provides it).

## Outputs
What this agent produces, and in what form (a diff, an ADR, a review report
with severities, a test suite, a risk list).

## Constraints
What this agent must never do — scope limits, irreversible actions it must
escalate rather than perform, patterns it must not introduce unilaterally.

## Workflow
Ordered steps this agent follows on a typical task. Reference the relevant
`workflows/*.md` file(s) rather than duplicating them.

## Tools It May Need
Optional capabilities this agent benefits from (filesystem, shell, git,
database, MCP/retrieval) and what it does when one is unavailable — consult
`AGENTS.md` §2 rather than restating the fallback table here.

## Skills to Load
- **Default (dotnet track):** list of `dotnet.*` skill ids this agent loads
  for a typical task in this role.
- **Default (agentic-ai track):** list of `agentic-ai.*` skill ids this
  agent loads when the task is classified as agentic-AI (see `AGENTS.md`
  §5). Leave empty and say "not applicable" if this role has no agentic-AI
  responsibility.
- **Task-specific:** how this agent resolves additional skills via
  `index/skills.yaml` beyond the defaults above.

## Validation Criteria
How this agent (or a reviewer) checks its own output is correct before
handing off — a checklist, not a vague "review your work."

## Failure / Escalation Conditions
When this agent should stop and hand off — to another agent (list which,
matching `escalates_to`), or to the user (per `AGENTS.md` §7).
