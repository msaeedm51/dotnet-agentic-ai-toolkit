---
id: dotnet.architecture.result-rop
title: Result Pattern / Railway-Oriented Programming
category: skill
domain: dotnet
technologies: [dotnet, csharp]
triggers: [result pattern, railway oriented programming, avoid exceptions for control flow, functional error handling]
requires: []
related: [dotnet.architecture.clean-architecture, dotnet.csharp, dotnet.api-design]
optional: []
prerequisites: []
tags: [architecture, error-handling]
---

# Result Pattern / Railway-Oriented Programming

## Purpose
Make expected failures part of a method's signature instead of hidden
control flow via exceptions, so callers must explicitly handle failure and
the happy path stays readable.

## When to Use
- Expected, "business" failures: validation failure, not-found, conflict,
  business rule rejection.
- Not for truly exceptional/unexpected conditions (out of memory, broken
  invariant, programming error) — those should still throw.

## Prerequisites
None.

## Inputs Required
Which failures in the operation are expected (part of the contract) vs.
truly exceptional (a bug or unrecoverable condition).

## Engineering Principles
1. Exceptions are for the exceptional; expected failures are values.
2. A `Result`/`Result<T>` return type makes "this can fail" visible in the
   signature — callers can't ignore it without an explicit unwrap.
3. Chain operations ("railway") so failure short-circuits without nested
   if-checks at every step.
4. Never use exceptions for normal control flow (e.g. throwing
   `NotFoundException` and catching it two layers up as the primary way to
   signal "not found" to an API layer that turns it into a 404) — return a
   `Result` and let the boundary map it explicitly.

## Step-by-Step Workflow
1. Define `Result` (no value) and `Result<T>` (with value) types — success/
   failure plus a failure reason.
2. Return `Result`/`Result<T>` from application/domain operations that have
   expected failure modes.
3. Chain with `Bind`/`Map`/`Match`-style combinators to avoid nested
   conditionals.
4. At the API boundary, map `Result` failures to the appropriate HTTP status
   / `ProblemDetails` (`dotnet.api-design`) — this is the one place a
   `Result` becomes an exception or an HTTP response, not scattered
   throughout the call stack.

## Code Standards
- `Result` types are immutable; failure carries a structured reason (error
  code + message), not just a string, if consumers need to branch on it.
- Don't mix styles within one call chain — a method returning `Result<T>`
  should not also throw for the same class of expected failure.

## Architecture Constraints
Domain/application layers return `Result`; only the outermost boundary
(API, background job runner) converts a failure into an HTTP response, log
entry, or retry decision.

## Security Considerations
Failure messages returned to external callers must not leak internal
details (stack traces, SQL, internal identifiers) — map to a safe external
message at the boundary (`dotnet.security`).

## Testing Requirements
Test both the success and failure `Result` for every operation with an
expected failure mode — a missing failure-case test is a coverage gap
(`rules/testing.md`).

## Common Mistakes
- Using `Result` for everything, including truly exceptional conditions,
  forcing every caller to check a failure that should never realistically
  happen.
- Silently discarding a `Result`'s failure state (not checking
  `IsSuccess`) — treat an unchecked `Result` as a bug, ideally caught by
  marking the type `[MustUseReturnValue]`-equivalent or an analyzer.

## Anti-Patterns
- **Result-wrapped exceptions**: catching an exception just to wrap it in a
  `Result.Failure(ex.Message)` without adding any value over letting it
  propagate — only do this at a boundary that needs the conversion.
- **Boolean blindness**: returning `bool` instead of `Result` for an
  operation that can fail for multiple distinguishable reasons.

## Validation Checklist
- [ ] Expected failures return `Result`/`Result<T>`; exceptions are reserved
      for truly exceptional conditions.
- [ ] Every `Result`-returning call site checks the result before using the
      value.
- [ ] Failure reasons don't leak internal detail across a trust boundary.

## Definition of Done
Meets `rules/definition-of-done.md`; both success and failure paths of a
new `Result`-returning operation are tested.

## Example
```csharp
public readonly struct Result
{
    public bool IsSuccess { get; }
    public string? Error { get; }
    public bool IsFailure => !IsSuccess;

    private Result(bool isSuccess, string? error) => (IsSuccess, Error) = (isSuccess, error);
    public static Result Success() => new(true, null);
    public static Result Failure(string error) => new(false, error);
}

public readonly struct Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }

    private Result(bool isSuccess, T? value, string? error) => (IsSuccess, Value, Error) = (isSuccess, value, error);
    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}

// API boundary maps Result -> HTTP, once, not scattered through the call stack
var result = await handler.Handle(command, ct);
return result.IsSuccess
    ? Results.Ok()
    : Results.Problem(detail: result.Error, statusCode: StatusCodes.Status400BadRequest);
```

## Related Skills
- `dotnet.architecture.clean-architecture` — where `Result`-returning
  handlers live.
- `dotnet.api-design` — mapping `Result` failures to `ProblemDetails`.
