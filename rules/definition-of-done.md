---
id: rule.definition-of-done
title: Definition of Done
category: rule
tech_tags: []
triggers: [is this done, definition of done, completion checklist, ready to merge]
severity: blocking
tags: [definition-of-done, completion]
---

# Definition of Done

A task is not complete until every applicable item below is true. This is
the universal baseline referenced by every agent, skill, and workflow in
this toolkit — skill-specific Definition of Done sections add to this, they
don't replace it.

## Requirements understood

**Rule:** The requirement has been restated (even briefly) and any
ambiguity materially affecting architecture or correctness has been
resolved — not guessed at (`rules/anti-hallucination.md`).

**Why:** Work against a misunderstood requirement is wasted regardless of
how well it's executed.

**Applies to:** Every task.

**Exception:** None.

---

## Architecture respected

**Rule:** The change follows the project's existing architecture and
`rules/architecture.md`; any deliberate deviation is stated and justified,
not silent.

**Why:** Unstated architecture drift accumulates into an inconsistent
codebase no one can reason about.

**Applies to:** Every task.

**Exception:** A task explicitly scoped as an architecture change.

---

## Implementation complete

**Rule:** The change does what was asked, with no partial/stubbed-out
paths left silently incomplete (a `TODO` for genuinely out-of-scope future
work is fine if flagged; a silently unhandled case is not).

**Why:** A partial implementation that looks complete is worse than an
honest "not yet" — it fails at the worst time.

**Applies to:** Every task.

**Exception:** None.

---

## Tests added/updated

**Rule:** Every behavior change has a test that fails without the change
and passes with it, per `rules/testing.md` (or `agentic-ai.evaluation` for
agent/LLM behavior).

**Why:** Untested behavior regresses silently the next time someone touches
the area.

**Applies to:** Every behavior change.

**Exception:** A project with `require_tests: false` in `.ai/config.yaml`
— still flag the gap.

---

## Security considered

**Rule:** Any change touching auth, input handling, data exposure, or (for
agentic-AI) prompt/tool boundaries has been checked against
`rules/security.md` / `rules/agentic-ai.md`, with a security-reviewer
escalation where warranted.

**Why:** Security issues found post-merge are far more expensive than ones
caught in the same change.

**Applies to:** Any change touching a security-relevant boundary.

**Exception:** Changes with no security-relevant surface (e.g. a pure
documentation update).

---

## Performance considered

**Rule:** A change with a plausible performance impact (new query, new
loop over external data, new hot-path allocation) has been reasoned about,
even if not formally benchmarked.

**Why:** Performance regressions are cheaper to prevent than to diagnose
after the fact in production.

**Applies to:** Changes with a plausible performance-sensitive surface.

**Exception:** Changes with no realistic performance impact.

---

## Logging/observability considered

**Rule:** A change that introduces a new failure mode or external call has
appropriate logging/tracing so it's debuggable in production
(`dotnet.dotnet`, `agentic-ai.observability`).

**Why:** An unobservable failure is undiagnosable the first time it
happens in production.

**Applies to:** New external calls, new background processes, new agent
behavior.

**Exception:** Purely internal, side-effect-free logic changes.

---

## Documentation updated where required

**Rule:** Setup steps, public contracts, or architecture decisions affected
by the change are reflected in documentation (`dotnet.documentation`), and
only there — no speculative documentation for unaffected areas.

**Why:** Stale documentation actively misleads the next reader.

**Applies to:** Changes affecting setup, a public contract, or a
significant architecture decision.

**Exception:** Changes with no user- or developer-facing documentation
impact.

---

## Build passes

**Rule:** The project builds cleanly with no new warnings introduced that
the project's configuration treats as significant.

**Why:** A build that "mostly" passes erodes the signal of the build status
for everyone.

**Applies to:** Every task where a build is possible in the current
environment.

**Exception:** Environments with no build access — state this explicitly
rather than claiming an unverified pass (`AGENTS.md` §2).

---

## Tests pass

**Rule:** The full relevant test suite passes, not just the new tests added
for this change.

**Why:** A change that breaks unrelated tests is a regression, whether or
not it was the intended target.

**Applies to:** Every task where tests can be run in the current
environment.

**Exception:** Environments with no test-execution access — state this
explicitly.

---

## No unrelated changes

**Rule:** The diff contains only what the task required — no drive-by
refactors, formatting-only changes to untouched files, or unrelated
cleanup bundled in.

**Why:** Unrelated changes make the diff harder to review and harder to
revert independently if something goes wrong.

**Applies to:** Every task.

**Exception:** A change the user explicitly asked to bundle.

---

## Deployment impact identified

**Rule:** Any change with a deployment implication (migration, new
configuration, new external dependency, breaking API change) has that
implication stated explicitly, including rollback considerations.

**Why:** A deployment surprise discovered during rollout is far more
expensive than one identified during review.

**Applies to:** Changes with a deployment-relevant surface.

**Exception:** Changes with no deployment impact.
