---
id: dotnet.typescript
title: TypeScript
category: skill
domain: dotnet
technologies: [typescript]
triggers: [typescript, strict typing, type safety, generics typescript]
requires: []
related: [dotnet.react, dotnet.api-design]
optional: []
prerequisites: []
tags: [typescript, frontend]
---

# TypeScript

## Purpose
Use TypeScript's type system to catch integration errors with the .NET
backend at compile time — matching API contracts exactly, not just writing
JavaScript with type annotations sprinkled on.

## When to Use
Any TypeScript file in a project with a frontend/tooling layer
(`.ai/config.yaml` → `frontend.language: typescript`).

## Prerequisites
None.

## Inputs Required
The backend API contract (`dotnet.api-design`) this code integrates with,
if applicable.

## Engineering Principles
1. `strict` mode enabled — no implicit `any`, strict null checks. Don't
   weaken `tsconfig.json` strictness to make an error go away; fix the
   actual type issue.
2. Types mirror the API contract exactly — a field that's optional/nullable
   on the backend is optional/nullable in the TypeScript type too, not
   assumed always-present.
3. Discriminated unions for state that has genuinely distinct shapes
   (loading/error/success), not one object with a lot of optional fields.
4. `unknown` over `any` for genuinely unknown external data (e.g. a caught
   exception, a third-party response) — forces a type check/narrowing
   before use.
5. Avoid type assertions (`as T`) as a way to silence the compiler instead
   of fixing an actual type mismatch — a wrong assertion just moves the bug
   to runtime.

## Step-by-Step Workflow
1. Confirm `tsconfig.json` has `strict: true` (and flag it if not, rather
   than writing code as if it were).
2. Define/import types matching the API contract precisely, including
   optionality and nullability.
3. Model distinct states as discriminated unions when a value can be one of
   several genuinely different shapes.
4. Narrow `unknown` values with type guards before use, rather than
   asserting a type.
5. Avoid `any` in new code; if a third-party library's types are incomplete,
   scope the workaround narrowly rather than disabling checking broadly.

## Code Standards
No `// @ts-ignore` without a comment explaining why and what would need to
change to remove it. No `any` in new code without an explicit, stated
reason.

## Architecture Constraints
Shared types between frontend and backend (if generated from OpenAPI or
otherwise shared) are the single source of truth for the contract shape —
don't hand-maintain a second, potentially drifting copy.

## Security Considerations
TypeScript's type system is not a security boundary — validate data from
genuinely untrusted sources (user input, third-party APIs) at runtime too,
not just at the type level.

## Testing Requirements
Type-level correctness is checked by the compiler; runtime behavior still
needs tests (`dotnet.react` for component-level testing).

## Common Mistakes
- Using `any` to make a type error disappear instead of fixing the actual
  mismatch.
- Modeling an API response type as if every field is always present when
  the backend contract says some are optional/nullable.
- Type assertions (`as SomeType`) papering over a shape mismatch that
  surfaces as a runtime error later.

## Anti-Patterns
- **`any` creep**: one `any` at a boundary silently propagating loss of
  type safety through everything downstream that touches it.
- **God interface**: one large interface with many optional fields
  representing several different logical states, instead of a
  discriminated union.

## Validation Checklist
- [ ] `strict` mode enabled.
- [ ] No unexplained `any` or `@ts-ignore`.
- [ ] Types match the backend contract's actual optionality/nullability.
- [ ] Distinct states modeled as discriminated unions where appropriate.

## Definition of Done
Meets `rules/definition-of-done.md`; `tsc` reports no errors under strict
mode for the changed code.

## Example
```typescript
type OrderSummary = {
  id: string;
  status: "Draft" | "Submitted" | "Cancelled"; // matches backend enum exactly
  total: number;
};

type FetchState<T> =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "success"; data: T };

function renderOrderSummary(state: FetchState<OrderSummary>): string {
  switch (state.kind) {
    case "loading": return "Loading…";
    case "error": return `Error: ${state.message}`;
    case "success": return `Order ${state.data.id}: ${state.data.status}`;
  }
}
```

## Related Skills
- `dotnet.react` — the framework layer this type discipline supports.
- `dotnet.api-design` — the contract these types must match exactly.
