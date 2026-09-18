---
id: dotnet.react
title: React for a .NET-Backed Frontend
category: skill
domain: dotnet
technologies: [react, typescript]
triggers: [react component, frontend for this api, state management, react forms, react error handling]
requires: [dotnet.typescript]
related: [dotnet.api-design, dotnet.authentication]
optional: []
prerequisites: [dotnet.typescript]
tags: [react, frontend]
---

# React for a .NET-Backed Frontend

## Purpose
Build a React frontend that consumes a .NET API correctly: typed API
integration, sane state management, and consistent error/loading handling
— not React in the abstract, but React as the client of the APIs this
toolkit's other skills produce.

## When to Use
The project has a React frontend (`.ai/config.yaml` → `frontend.framework:
react`). Not assumed for every .NET project.

## Prerequisites
`dotnet.typescript`.

## Inputs Required
The API contract it's consuming (from `dotnet.api-design`) and the
authentication mechanism the frontend must implement (token storage,
refresh).

## Engineering Principles
1. Type the API contract on the frontend (generated from the OpenAPI spec
   if available, or hand-written types matching the backend DTOs exactly)
   — never `any` for API response shapes.
2. Server state (data fetched from the API) is managed differently from
   client/UI state — a data-fetching library (e.g. React Query/TanStack
   Query) for the former, `useState`/context for the latter; don't put
   server data in a global client-state store by default.
3. Every data-fetching component handles three states explicitly: loading,
   error, and success — never assume the happy path.
4. Forms validate client-side for UX and rely on the server's validation as
   the actual authority — a client-only validation is not a security
   boundary (`dotnet.security`).
5. Accessibility (semantic HTML, keyboard navigation, ARIA where semantic
   HTML isn't enough) is part of the component, not an afterthought pass.

## Step-by-Step Workflow
1. Define/import the TypeScript types matching the API's request/response
   DTOs.
2. Build the data-fetching hook (React Query or equivalent) with explicit
   loading/error/success handling.
3. Build the component consuming that hook, rendering each state
   distinctly (skeleton/spinner for loading, an actionable error message
   for error, real content for success).
4. Wire authentication: attach the token to requests, handle 401 (redirect
   to login / refresh token) consistently via a shared HTTP client
   interceptor, not per-component.
5. Add accessibility basics: semantic elements, labeled form fields,
   keyboard-operable interactive elements.

## Code Standards
Components are function components with typed props; no implicit `any`.
API calls go through a shared, typed client module, not `fetch` calls
scattered inline across components.

## Architecture Constraints
Components don't construct raw API URLs inline — a shared API client
module owns the base URL, auth header attachment, and error normalization.

## Security Considerations
Tokens are stored per `dotnet.authentication`'s guidance (prefer httpOnly
cookies over `localStorage` for anything sensitive, if the auth flow
supports it). Never render unescaped user-generated content with
`dangerouslySetInnerHTML` without sanitization (XSS).

## Testing Requirements
Component tests (React Testing Library) covering loading, error, and
success states for any data-fetching component; not just a snapshot of the
happy path.

## Common Mistakes
- `any`-typed API responses, silently breaking type safety at the exact
  boundary where it matters most.
- No error state handling — a failed request leaves the UI stuck on a
  spinner or shows nothing.
- Storing a sensitive token in `localStorage` without considering XSS
  exposure.

## Anti-Patterns
- **Prop drilling for server state**: threading fetched data through many
  component layers instead of a data-fetching hook colocated with the
  component that needs it.
- **Global store for everything**: putting all server state into Redux/a
  global store when a data-fetching library already handles caching/
  invalidation more appropriately.

## Validation Checklist
- [ ] API response types match the backend contract, no `any`.
- [ ] Loading, error, and success states are all handled explicitly.
- [ ] Auth token attachment and 401 handling are centralized.
- [ ] Forms are validated client-side for UX, server-side for correctness.

## Definition of Done
Meets `rules/definition-of-done.md`; component tests cover loading/error/
success states.

## Example
```tsx
function useOrderSummary(orderId: string) {
  return useQuery<OrderSummary, ApiError>({
    queryKey: ["order-summary", orderId],
    queryFn: () => apiClient.get<OrderSummary>(`/orders/${orderId}`),
  });
}

function OrderSummaryView({ orderId }: { orderId: string }) {
  const { data, isLoading, isError, error } = useOrderSummary(orderId);

  if (isLoading) return <Skeleton />;
  if (isError) return <ErrorBanner message={error.message} />;
  return <OrderSummaryCard summary={data} />;
}
```

## Related Skills
- `dotnet.typescript` — language-level conventions this relies on.
- `dotnet.api-design` — the contract this frontend consumes.
- `dotnet.authentication` — token handling on the client.
