<!--
Canonical skill template. Copy this file, fill every section, delete this
comment block. Do not leave a header with no content — if a section
genuinely doesn't apply, delete the header and say why in the PR.
See _meta/frontmatter-schema.md for the frontmatter contract.
-->
---
id: <domain>.<category>.<skill-name>
title: <Human-readable title>
category: skill
domain: dotnet | agentic-ai
technologies: []
triggers: []
requires: []
related: []
optional: []
prerequisites: []
tags: []
---

# <Skill Title>

## Purpose
One paragraph: what engineering problem this skill solves and why it exists
as its own skill rather than being folded into another one.

## When to Use
Bullet list of concrete request shapes that should trigger this skill. These
should closely match `triggers` in the frontmatter.

## Prerequisites
What the AI assistant (or reader) needs to already know or have available —
cross-reference `prerequisites` and `requires` from frontmatter here in
prose, plus any non-skill prerequisite (e.g. "the project must already have
a working DI container").

## Inputs Required
What information must be known before applying this skill — from the
project, from `.ai/config.yaml`, or from the user. Distinguish what can be
discovered by inspecting the project vs. what must be asked.

## Engineering Principles
The non-negotiable principles behind this skill — short, numbered, each one
independently defensible. Not a rehash of `rules/*.md`; principles specific
to this skill's domain.

## Step-by-Step Workflow
Ordered steps to apply this skill to a real task. Concrete enough that an AI
assistant could follow it without additional interpretation.

## Code Standards
Concrete conventions for this skill's area — naming, structure, idioms.
Reference `rules/csharp.md` / `rules/dotnet.md` rather than repeating them;
only list what's specific to this skill.

## Architecture Constraints
Boundaries this skill must respect (dependency direction, layer placement,
module ownership). Reference `rules/architecture.md` for the general rules;
state only what's specific here.

## Security Considerations
What this skill must never get wrong from a security standpoint. If none
apply beyond the general baseline, say so explicitly and point to
`rules/security.md` (or `rules/agentic-ai.md` for agentic-AI skills) rather
than leaving this section empty.

## Testing Requirements
What must be tested when this skill is applied, and at what level (unit,
integration, contract, evaluation). Be specific — "test the failure path
when X" not "write good tests."

## Common Mistakes
Realistic mistakes an experienced engineer still makes in this area, and why
they happen.

## Anti-Patterns
Named patterns to actively avoid, with the concrete failure mode each one
causes. Distinct from Common Mistakes: these are things that look
intentional but are wrong.

## Validation Checklist
A checklist the AI assistant (or a human reviewer) can run through
mechanically before calling the work done in this skill's area.

## Definition of Done
Skill-specific completion criteria, in addition to (not instead of)
`rules/definition-of-done.md`.

## Example
At least one realistic, production-style example in modern C#/.NET (or the
relevant stack) — realistic naming, real error handling, and a test. Include
a short note on the trade-off the example makes, if any.

## Related Skills
List with one-line reason for each, matching `related`/`requires`/`optional`
in frontmatter — this is the human-readable mirror of that metadata.
