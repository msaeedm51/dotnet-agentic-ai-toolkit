---
id: dotnet.documentation
title: Documentation Standards
category: skill
domain: dotnet
technologies: [dotnet]
triggers: [write documentation, adr, api documentation, runbook, readme]
requires: []
related: []
optional: []
prerequisites: []
tags: [documentation]
---

# Documentation Standards

## Purpose
Produce documentation that stays accurate and useful — scoped to what
actually needs it, not documentation for its own sake. See
`agents/documentation-engineer.md` for the role that applies this skill.

## When to Use
Per `rules/definition-of-done.md` — when a change affects setup steps, a
public contract, an architectural decision worth recording, or an
operational procedure.

## Prerequisites
None.

## Inputs Required
What actually changed that documentation needs to reflect, and who the
reader is (another engineer, an operator during an incident, an external
API consumer).

## Engineering Principles
1. Document for the reader who has to act on it — an operator during an
   incident needs a runbook's exact commands, not architecture rationale.
2. Keep documentation next to what it describes when possible (README near
   the code, API docs generated from the contract) so it's more likely to
   be updated when the thing changes.
3. An ADR records a decision at the time it was made — context, decision,
   alternatives, consequences — and is not edited after the fact to look
   like it always said the current thing; a changed decision gets a new
   ADR that supersedes the old one.
4. Don't document what's self-evident from well-named code — comments and
   docs earn their place by adding something the code alone doesn't convey.

## Step-by-Step Workflow
1. Identify the audience and purpose: setup guide, API reference, ADR,
   runbook, or feature documentation.
2. Verify the current behavior/setup steps against the actual code before
   writing — don't document from memory of how it used to work.
3. Write for the specific reader's need — a runbook is a checklist of
   exact steps, an ADR is a decision record, a README is "how do I get this
   running."
4. Link related documentation instead of duplicating its content.
5. For an ADR, use the standard shape: Status, Context, Decision,
   Alternatives, Consequences, Risks.

## Code Standards
Not applicable directly — see `AGENTS.md`/root style guidance: comments in
code explain non-obvious "why," not "what."

## Architecture Constraints
Not applicable.

## Security Considerations
Documentation (especially runbooks/architecture docs) must not include
live secrets, real credentials, or production connection details in
plaintext — use placeholders and reference the secret store.

## Testing Requirements
Not applicable directly; documentation accuracy is verified against current
code as part of the workflow above, not tested automatically (except
generated API docs, which are verified by regenerating them from source).

## Common Mistakes
- Writing documentation once and never updating it as the code changes,
  letting it silently drift into being wrong.
- An ADR that's really just a description of the code, with no actual
  context/alternatives/trade-off discussion.
- Documenting implementation detail that belongs in a code comment instead,
  duplicating information that will drift from the code.

## Anti-Patterns
- **Documentation for its own sake**: creating a document because a
  template exists, not because a reader needs it.
- **Stale documentation left standing**: an outdated doc that's actively
  misleading, left in place because updating it "wasn't part of this
  change" — if you touched the behavior it describes, update it.

## Validation Checklist
- [ ] Documentation reflects the current code, verified, not remembered.
- [ ] Written for the actual reader's need (setup, reference, decision
      record, operational procedure).
- [ ] No live secret/credential included.
- [ ] Only created where a workflow/rule actually requires it.

## Definition of Done
Meets `rules/definition-of-done.md`.

## Example
```markdown
# ADR-0007: Use the Outbox Pattern for Order Integration Events

## Status
Accepted

## Context
Order submission needs to notify Inventory and Billing reliably. Publishing
directly to the message broker after SaveChangesAsync risked losing events
on a crash between commit and publish.

## Decision
Write integration events to an OutboxMessages table in the same transaction
as the order state change; a background worker publishes and marks them sent.

## Alternatives Considered
- Publish-then-commit: rejected, can publish an event for a transaction that
  then fails to commit.
- Two-phase commit with the broker: rejected, not supported by our broker
  and adds significant complexity.

## Consequences
Adds an outbox table and a background publisher. Consumers must be
idempotent (at-least-once delivery).

## Risks
Publisher lag under high load; mitigated by monitoring outbox backlog depth.
```

## Related Skills
None beyond the general documentation workflow this skill defines.
