---
id: dotnet.csharp
title: Modern C#
category: skill
domain: dotnet
technologies: [csharp, dotnet8, dotnet9]
triggers: [c# language features, nullable reference types, records, pattern matching, modern c#]
requires: []
related: [dotnet.dotnet, dotnet.architecture.result-rop]
optional: []
prerequisites: []
tags: [csharp, language]
---

# Modern C#

## Purpose
Write idiomatic, safe, modern C# — nullable reference types enabled,
records/pattern matching used where they reduce ceremony, async used
correctly for I/O — as the language-level baseline every other skill in
this toolkit assumes.

## When to Use
Every C# file. This is the language baseline `rules/csharp.md` enforces;
this skill is the "how," the rules file is the "must."

## Prerequisites
None.

## Inputs Required
None beyond the code being written/changed.

## Engineering Principles
1. Nullable reference types are enabled and respected — a `string` means
   never null, `string?` means it can be. Don't suppress warnings with `!`
   to silence the compiler instead of fixing the actual nullability.
2. Prefer explicit domain types over primitive obsession (`OrderId` over a
   bare `Guid`, `Email` over a bare `string`) where the type carries
   validation or meaning.
3. Records for immutable data; classes for identity/behavior-bearing types.
4. Pattern matching (`switch` expressions, property patterns) over chained
   `if`/`else` for shape-based branching.
5. Async all the way for I/O-bound work; never block on async code with
   `.Result`/`.Wait()` (deadlock risk, thread-pool starvation).
6. `CancellationToken` flows through any long-running or request-bound
   async call chain.
7. Avoid unnecessary allocations in hot paths (`Span<T>`, avoid LINQ in
   tight loops if profiling shows it matters — don't micro-optimize without
   evidence).

## Step-by-Step Workflow
1. Confirm nullable reference types are enabled (`<Nullable>enable</Nullable>`
   in the project file) — if not, that's a project-level gap to flag, not
   silently work around.
2. Model data with the right construct: `record`/`record struct` for
   immutable value-like data, `class` for entities with identity and
   behavior.
3. Use explicit domain types for anything with validation rules or where a
   bare primitive is easy to misuse (swapping two `Guid` parameters).
4. Write async methods with `Async` suffix, accept `CancellationToken` as
   the last parameter, and propagate it to every downstream async call.
5. Prefer pattern matching over type-checking + casting chains.

## Code Standards
- File-scoped namespaces, primary constructors where they reduce
  boilerplate without hurting readability.
- `sealed` by default on classes not designed for inheritance.
- No `async void` except event handlers.
- No `.Result`/`.Wait()`/`.GetAwaiter().GetResult()` on the request path.

## Architecture Constraints
Language-level; no cross-layer constraint of its own, but respects whatever
layer it's used in (`dotnet.architecture.clean-architecture`).

## Security Considerations
Nullable reference types reduce null-reference-triggered crashes but are
not a security boundary — still validate untrusted input explicitly
(`dotnet.security`).

## Testing Requirements
Unit-testable by construction if types are immutable and side-effect-free
where possible; test both branches of any pattern match with more than one
meaningful case.

## Common Mistakes
- Suppressing a nullable warning with `!` instead of fixing the actual flow.
- Bare `Guid`/`string` parameters where a wrong-order call compiles silently
  (`CreateOrder(Guid customerId, Guid productId)` — easy to swap).
- Blocking on async (`.Result`) "just this once" in a non-async caller —
  causes deadlocks in ASP.NET Core's synchronization context in enough
  cases to always avoid it; make the caller async instead.

## Anti-Patterns
- **Stringly-typed code**: using raw strings for identifiers, statuses, or
  enums that should be a real type.
- **God-class services**: static classes holding unrelated mutable state,
  making testing and reasoning about concurrency hard.

## Validation Checklist
- [ ] Nullable reference types enabled and no unjustified `!` suppressions.
- [ ] No `.Result`/`.Wait()` on async code.
- [ ] `CancellationToken` accepted and propagated on I/O-bound async
      methods.
- [ ] Explicit domain types used where primitive obsession would risk bugs.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/csharp.md`.

## Example
```csharp
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

public sealed class OrderService(IOrderRepository repository)
{
    public async Task<Result<OrderId>> CreateAsync(CreateOrderRequest request, CancellationToken ct)
    {
        var validation = request switch
        {
            { CustomerId: var id } when id == Guid.Empty => Result.Failure("CustomerId is required."),
            { Lines.Count: 0 } => Result.Failure("At least one line is required."),
            _ => Result.Success()
        };

        if (validation.IsFailure)
            return Result<OrderId>.Failure(validation.Error!);

        var order = Order.Create(request.CustomerId, request.Lines);
        await repository.SaveAsync(order, ct);
        return Result<OrderId>.Success(order.Id);
    }
}
```

## Related Skills
- `dotnet.dotnet` — runtime/framework layer this language sits on.
- `dotnet.architecture.result-rop` — the `Result` pattern used above.
