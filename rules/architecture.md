---
id: rule.architecture
title: Architecture Rules
category: rule
tech_tags: [dotnet]
triggers: [architecture rules, dependency direction rule, simplest architecture, module boundary rule]
severity: blocking
tags: [architecture]
---

# Architecture Rules

## Respect dependency direction

**Rule:** Dependencies point inward (Infrastructure → Application →
Domain); Domain never references Infrastructure or a specific framework
package (`dotnet.architecture.clean-architecture`).

**Why:** This is what keeps business logic testable and framework-
independent — violating it once tends to cascade into a codebase where
domain and infrastructure are inseparable.

**Applies to:** Projects following Clean Architecture / DDD layering.

**Exception:** A project that has explicitly and deliberately chosen not to
layer this way (e.g. a small script/tool) — state this explicitly, don't
silently skip the rule.

---

## Domain must not depend on Infrastructure

**Rule:** No domain-layer type references EF Core, a specific HTTP client,
or any other infrastructure package, directly or transitively.

**Why:** This is the concrete, checkable form of the dependency-direction
rule above — enforce it with an architecture test
(`dotnet.testing`), not just code review.

**Applies to:** Any project with a Domain layer.

**Exception:** None.

---

## Avoid cross-module database access where boundaries prohibit it

**Rule:** In a modular monolith or microservices architecture, no module/
service queries another's tables directly — cross-boundary interaction goes
through the owning module's public contract or events
(`dotnet.architecture.modular-monolith`).

**Why:** Direct cross-boundary data access recreates tight coupling the
module/service boundary was meant to prevent, and makes the boundary
impossible to extract or evolve independently later.

**Applies to:** Modular monoliths and microservices.

**Exception:** A deliberately shared read model/reporting database that's
explicitly designed and documented as a cross-boundary contract, not an
accidental leak.

---

## Do not introduce a pattern merely because it is fashionable

**Rule:** A pattern (CQRS, event sourcing, microservices, a new
abstraction layer) is adopted because a concrete requirement drives it —
stated explicitly — not because it's considered best practice in the
abstract.

**Why:** Every pattern has a complexity cost; paying it without the
corresponding benefit makes the codebase harder to work in for no reason.

**Applies to:** Every architectural pattern decision.

**Exception:** None — if there's no concrete driver, use the simpler
alternative.

---

## Prefer the simplest architecture that satisfies requirements

**Rule:** When multiple architectures would satisfy the actual
requirement, choose the simplest one; escalate to `agent.architect` before
committing to a more complex one.

**Why:** Complexity taken on speculatively (for hypothetical future scale
or flexibility) is a cost paid immediately for a benefit that may never
materialize.

**Applies to:** Every architecture decision.

**Exception:** A stated, concrete near-term requirement justifies the more
complex option.

---

## An aggregate is the unit of transactional consistency

**Rule:** A single transaction modifies at most one aggregate; consistency
across aggregates is eventual, coordinated via domain/integration events
(`dotnet.architecture.ddd`, `.domain-events-outbox`).

**Why:** Transactions spanning multiple aggregates create contention and
make the aggregate boundary meaningless as a consistency guarantee.

**Applies to:** DDD-modeled domains.

**Exception:** None — if two things must always be consistent together,
they're one aggregate, not two coordinated by a cross-aggregate
transaction.
