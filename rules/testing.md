---
id: rule.testing
title: Testing Rules
category: rule
tech_tags: [xunit, testcontainers]
triggers: [testing rules, test coverage rule, negative test rule, mocking rule]
severity: blocking
tags: [testing]
---

# Testing Rules

## Every business rule must have tests

**Rule:** A domain invariant or business rule has at least one test proving
it's enforced and at least one proving the invalid case is rejected.

**Why:** An untested business rule regresses silently the first time
someone touches the surrounding code.

**Applies to:** Every business rule/domain invariant.

**Exception:** None.

---

## Test failure paths

**Rule:** For every operation with a defined failure mode (validation
failure, not-found, conflict), a test exercises that failure mode, not just
the success path.

**Why:** The failure path is exactly the code least likely to be exercised
by casual manual testing, and most likely to matter when it's hit in
production.

**Applies to:** Every operation with a defined failure mode.

**Exception:** None.

---

## Test authorization boundaries

**Rule:** Every authorization policy has a test proving the allowed case
succeeds and a test proving the denied case is actually rejected (403/401),
not silently allowed.

**Why:** A missing authorization test is how a broken/missing check ships
to production undetected.

**Applies to:** Every authorization policy.

**Exception:** None.

---

## Do not test implementation details unnecessarily

**Rule:** Tests assert on observable behavior/contract, not internal
implementation structure that could change without changing behavior.

**Why:** Over-specified tests break on harmless refactors, training the
team to ignore test failures instead of trusting them.

**Applies to:** Every test.

**Exception:** A test explicitly targeting an implementation detail that's
itself part of the contract (e.g. verifying a specific SQL query shape for
a performance-critical path).

---

## Integration-test important infrastructure boundaries

**Rule:** A code path relying on real database/engine-specific behavior,
message broker semantics, or another real infrastructure boundary is
integration-tested against a real instance (Testcontainers), not just unit-
tested against a mock/in-memory substitute.

**Why:** A mock always behaves the way you told it to; it can't catch a
real constraint violation or query-translation failure.

**Applies to:** Any code relying on real infrastructure behavior.

**Exception:** None.

---

## Mock only genuine boundaries the test doesn't own

**Rule:** A test mocks a dependency only when that dependency is outside
what the test is meant to verify (a third-party payment gateway) — never
the system's own database/repository when the test's purpose is to verify
data access correctness.

**Why:** Mocking the thing you're trying to test defeats the test's
purpose; see `dotnet.testing` for the fuller reasoning.

**Applies to:** Every test with a mocked dependency.

**Exception:** None.
