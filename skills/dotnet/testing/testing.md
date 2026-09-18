---
id: dotnet.testing
title: Testing (Unit, Integration, API, Architecture)
category: skill
domain: dotnet
technologies: [xunit, webapplicationfactory, testcontainers, fluentassertions]
triggers: [write tests, unit test, integration test, api test, testcontainers, architecture test, test data]
requires: []
related: [dotnet.csharp, dotnet.efcore, dotnet.aspnetcore]
optional: []
prerequisites: []
tags: [testing, xunit]
---

# Testing (Unit, Integration, API, Architecture)

## Purpose
Verify behavior at the right level — unit tests for logic, integration
tests for real infrastructure boundaries, API tests for the HTTP contract,
architecture tests for structural rules — without over-mocking to the point
tests pass while production breaks.

## When to Use
Every behavior change needs a test per `rules/testing.md`. This skill
covers how; `agent.test-engineer` owns non-trivial test design.

## Prerequisites
None.

## Inputs Required
What kind of behavior is being tested (pure logic, a database interaction,
an HTTP endpoint, a structural architecture rule) — determines the right
test level.

## Engineering Principles
1. Unit tests for business rules and domain logic — no database, no HTTP,
   fast and deterministic.
2. Integration tests for real infrastructure boundaries that matter for
   correctness (database queries with engine-specific behavior, message
   broker interaction) — use Testcontainers for a real engine instance
   rather than a fake/in-memory substitute that doesn't enforce the same
   constraints.
3. API tests via `WebApplicationFactory` for the full HTTP pipeline
   (routing, model binding, validation, auth, serialization) — not just the
   handler logic in isolation.
4. Architecture tests (e.g. with a project like `NetArchTest`) to enforce
   structural rules (dependency direction, module boundaries) mechanically,
   not just by code review.
5. Mock only at a genuine boundary the test doesn't own (an external
   payment gateway) — mocking your own repository/database in a test meant
   to catch a real integration bug defeats the test's purpose.
6. Test negative and boundary cases explicitly: invalid input,
   unauthorized access, concurrent modification, not-found, empty
   collections.

## Step-by-Step Workflow
1. Classify the behavior under test: pure logic → unit test; infrastructure
   boundary → integration test; HTTP contract → API test; structural rule
   → architecture test.
2. For unit tests: construct the object under test directly, assert on its
   public behavior/`Result`, no framework bootstrapping.
3. For integration tests: spin up a real dependency via Testcontainers
   (SQL Server, PostgreSQL, a message broker), run the actual code path
   against it, tear down after.
4. For API tests: use `WebApplicationFactory<TEntryPoint>`, optionally
   overriding specific services (e.g. swap a real payment gateway for a
   test double) while keeping the real pipeline intact.
5. For architecture tests: assert dependency direction and module boundary
   rules as part of the normal test suite, so a violation fails CI.
6. Build test data with realistic, varied states — not just the minimal
   happy-path object — including edge values (empty, max length, boundary
   numbers).

## Code Standards
Test names describe behavior and scenario
(`Submit_WhenNoLines_ReturnsFailure`), not the method under test alone.
Arrange/Act/Assert (or Given/When/Then) structure, one logical assertion
focus per test.

## Architecture Constraints
Test projects may reference Infrastructure for integration tests; unit test
projects for Domain/Application should not need an Infrastructure
reference at all — if they do, that's a signal the unit under test isn't
actually isolated.

## Security Considerations
Test fixtures never contain real credentials/PII; use generated or
clearly-fake test data. Test databases/containers are isolated from
production.

## Testing Requirements
(This skill is itself about testing requirements — see
`rules/testing.md` for the enforceable rule list this skill implements.)

## Common Mistakes
- Mocking the repository in a test meant to verify a query actually returns
  correct results — the mock always returns what you tell it to, so the
  test can't catch a real query bug.
- Using EF Core's in-memory provider for integration tests, missing real
  constraint violations and SQL translation failures.
- Only testing the happy path, leaving failure/authorization paths
  unverified.

## Anti-Patterns
- **Over-mocked tests**: every collaborator mocked, so the test verifies
  the mocks were called correctly rather than that the system behaves
  correctly.
- **Slow unit tests**: a "unit" test that spins up a database or makes a
  network call — that's an integration test mislabeled, and it'll be
  skipped/ignored once the suite gets slow enough.
- **Snapshot-everything**: asserting on an entire large object graph
  instead of the specific fields the test is actually about, causing
  unrelated changes to break unrelated tests.

## Validation Checklist
- [ ] Test level matches what's actually being verified (unit/integration/
      API/architecture).
- [ ] Negative and boundary cases are covered, not just the happy path.
- [ ] Integration tests use a real engine (Testcontainers), not a fake.
- [ ] No mock hides the exact behavior the test is meant to catch.

## Definition of Done
Meets `rules/definition-of-done.md`; new/changed behavior has a test that
fails without the change and passes with it.

## Example
```csharp
public class SubmitOrderTests
{
    [Fact]
    public void Submit_WhenNoLines_ReturnsFailure()
    {
        var order = Order.Create(customerId: Guid.NewGuid(), lines: []);

        var result = order.Submit();

        result.IsFailure.Should().BeTrue();
        result.Error.Should().Be("Cannot submit an order with no lines.");
    }
}

public class OrdersApiTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task Post_WithoutAuth_Returns401()
    {
        var client = factory.CreateClient();
        var response = await client.PostAsJsonAsync("/orders", new { customerId = Guid.NewGuid(), lines = Array.Empty<object>() });
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }
}
```

## Related Skills
- `dotnet.csharp` — language-level testability considerations.
- `dotnet.efcore` — database testing detail (Testcontainers usage).
- `dotnet.aspnetcore` — `WebApplicationFactory` setup detail.
- `agentic-ai.evaluation` — the agentic-AI-track equivalent for agent/LLM
  behavior.
