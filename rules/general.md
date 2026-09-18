---
id: rule.general
title: General Rules
category: rule
tech_tags: []
triggers: [general rules, cross cutting rules, smallest change, avoid refactoring]
severity: blocking
tags: [general]
---

# General Rules

Cross-cutting rules not specific to a layer or technology. `AGENTS.md`
covers *how the AI should behave*; these are the enforceable rules that
behavior produces — checkable in a diff regardless of who/what wrote it.

## Make the smallest safe change

**Rule:** A change is scoped to exactly what the task requires — no
speculative generalization, no unrelated cleanup, no "while I'm here"
additions.

**Why:** Every line beyond what's needed is a line someone else has to
review, maintain, and reason about later for no corresponding benefit.

**Applies to:** Every change.

**Exception:** The user explicitly asks for a broader change.

---

## Do not introduce an abstraction without a concrete reason

**Rule:** A new interface, base class, or generic layer needs a stated,
concrete reason (an actual second implementation, a genuine testing need,
a real extensibility requirement) — not "this might be reused later."

**Why:** Speculative abstraction adds indirection cost immediately for a
benefit that may never materialize, and is harder to remove than to add.

**Applies to:** Every new abstraction.

**Exception:** A pattern the project has already standardized on
(e.g. every aggregate gets a repository interface, per
`dotnet.architecture.repository-specification`) — consistency itself is the
concrete reason there.

---

## Reuse existing abstractions

**Rule:** Before creating a new service, utility, or type, search for an
existing one that already does this or something close enough to extend.

**Why:** Duplicate abstractions for the same concern drift apart over time
and confuse future readers about which one is authoritative.

**Applies to:** Every new type/service.

**Exception:** The existing abstraction genuinely doesn't fit and adapting
it would be more invasive than the task warrants — state why.

---

## Avoid unnecessary dependencies

**Rule:** A new package dependency is justified against what's already
available in the project — don't add a package for something a few lines
of code or an existing dependency already covers.

**Why:** Every dependency is a standing cost: security surface, update
burden, licensing, and a new thing every contributor needs to know.

**Applies to:** Every new package reference.

**Exception:** The existing option is genuinely inadequate (missing
functionality, unmaintained, wrong license) — state why.

---

## Preserve existing behavior unless the requirement changes it

**Rule:** A change does not alter observable behavior beyond what the task
asked for. If an unrelated behavior change is unavoidable, it's called out
explicitly, not left for the reviewer to discover.

**Why:** An unannounced behavior change is the classic cause of "but I
didn't touch that" production incidents.

**Applies to:** Every change.

**Exception:** The task is explicitly a behavior change.

---

## Consider backward compatibility

**Rule:** A change to anything with external callers (a public API, a
published event schema, a shared library's public surface) considers
backward compatibility explicitly — breaking it requires a stated
versioning/migration plan, not silence.

**Why:** A silent breaking change fails for every consumer simultaneously,
often without warning.

**Applies to:** Any change to a contract with external/independent
consumers.

**Exception:** The contract is genuinely internal with no external
consumers — verify this, don't assume it.

---

## Explain non-obvious architectural decisions

**Rule:** When a choice isn't obvious from the diff alone (why this
pattern, why this boundary, why this trade-off), state the reasoning in the
response, not just in a comment buried in the code.

**Why:** A reviewer without the reasoning either has to guess or has to ask
— both cost more than stating it once, upfront.

**Applies to:** Any non-obvious design decision.

**Exception:** Decisions that are genuinely self-evident from well-named
code.

---

## Flag risks even outside the task's scope

**Rule:** A security or performance risk noticed while working on something
else is flagged explicitly (without expanding the change to fix it
uninvited).

**Why:** A known risk that's never surfaced because it wasn't the task at
hand is a missed opportunity to prevent a future incident cheaply.

**Applies to:** Any risk noticed during the course of a task.

**Exception:** None — flagging costs little; silently ignoring a known risk
does not.
