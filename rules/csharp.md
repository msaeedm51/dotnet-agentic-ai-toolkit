---
id: rule.csharp
title: C# Rules
category: rule
tech_tags: [csharp]
triggers: [c# rules, nullable reference types, async rules, cancellation token rule]
severity: blocking
tags: [csharp]
---

# C# Rules

## Enable nullable reference types

**Rule:** Every project has `<Nullable>enable</Nullable>`, and warnings are
not suppressed with `!` without a genuine, stated reason.

**Why:** Nullable reference types catch a large class of null-reference
bugs at compile time; suppressing them defeats the purpose.

**Applies to:** All C# projects in this toolkit's scope.

**Exception:** A specific, documented case where the compiler can't infer
non-null but the invariant is guaranteed by code the analyzer can't see.

---

## Prefer explicit domain types over primitive obsession

**Rule:** A value with validation rules or domain meaning (an id, an email,
a money amount) gets a real type instead of a bare primitive, where mixing
up two same-typed primitives would compile silently and cause a bug.

**Why:** `CreateOrder(Guid customerId, Guid productId)` compiles fine with
the arguments swapped; `CreateOrder(CustomerId customerId, ProductId
productId)` doesn't.

**Applies to:** Domain identifiers and validated values.

**Exception:** A value with no real domain meaning or validation rule (a
loop counter) doesn't need a wrapper type.

---

## Avoid unnecessary static state

**Rule:** Static mutable state is avoided; prefer instances managed by DI
with an explicit lifetime.

**Why:** Static mutable state is invisible in a constructor signature,
hard to test in isolation, and a common source of subtle concurrency bugs.

**Applies to:** All C# code.

**Exception:** Truly immutable static data (constants, static readonly
collections that never change).

---

## Prefer async APIs for I/O

**Rule:** Any I/O-bound operation (database, HTTP, file, message broker)
uses the async API, `await`ed, all the way up the call stack.

**Why:** Synchronous I/O blocks a thread for the duration of the call,
which doesn't scale under concurrent load.

**Applies to:** Any I/O-bound call.

**Exception:** A genuinely CPU-bound operation with no I/O has no reason to
be async.

---

## Never block async code with `.Result` or `.Wait()`

**Rule:** Async methods are never called synchronously via `.Result`,
`.Wait()`, or `.GetAwaiter().GetResult()` on a request-handling or
otherwise concurrency-sensitive path.

**Why:** This risks deadlocks under certain synchronization contexts and
always risks thread-pool starvation under load, even when it "works" in
manual testing.

**Applies to:** Any async call in application code.

**Exception:** A narrow, well-understood case at an application's true
entry point (e.g. `Main`) where no synchronization context is present —
even then, prefer `GetAwaiter().GetResult()` explicitly and document why.

---

## Use cancellation tokens for long-running/request-bound operations

**Rule:** Any method doing I/O or meaningful work accepts a
`CancellationToken` and propagates it to every downstream async call.

**Why:** Without it, a client disconnect or timeout can't actually stop the
work already in flight, wasting resources.

**Applies to:** Any I/O-bound or long-running method.

**Exception:** A method with no meaningful cancellation point (trivial,
synchronous, no I/O).

---

## Avoid unnecessary allocations

**Rule:** Hot-path code avoids unnecessary allocations (boxing, unneeded
LINQ materialization, repeated string concatenation) where profiling shows
it matters — this is not a default micro-optimization pass for cold paths.

**Why:** Allocation pressure in a genuinely hot path causes real GC
overhead; the same concern in a rarely-called path is wasted effort that
hurts readability for no benefit.

**Applies to:** Code identified as a hot path by profiling
(`dotnet.performance`).

**Exception:** Cold/rarely-executed paths, where clarity should win.

---

## Do not introduce an abstraction without a concrete reason

**Rule:** See `rules/general.md` — this applies at the language level too:
no interface with exactly one implementation and no stated reason for the
indirection.

**Why:** Restated here because it's a common C#-specific violation
(interface-per-class by habit).

**Applies to:** Every new interface/abstract class.

**Exception:** See `rules/general.md`.
