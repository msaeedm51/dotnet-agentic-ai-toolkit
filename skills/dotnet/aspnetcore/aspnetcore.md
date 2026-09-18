---
id: dotnet.aspnetcore
title: ASP.NET Core API Development
category: skill
domain: dotnet
technologies: [aspnetcore, dotnet8, dotnet9]
triggers: [create endpoint, minimal api, web api, controller, rest api, model validation, problemdetails]
requires: [dotnet.dotnet]
related: [dotnet.api-design, dotnet.authentication, dotnet.authorization, dotnet.testing]
optional: []
prerequisites: [dotnet.dotnet]
tags: [aspnetcore, api, minimal-api]
---

# ASP.NET Core API Development

## Purpose
Build HTTP endpoints — minimal APIs or controllers — that validate input at
the boundary, return predictable responses, and don't leak domain internals
to callers.

## When to Use
Any request to create or modify an ASP.NET Core endpoint. Pairs with
`dotnet.api-design` for contract-level rules (status codes, versioning) —
this skill is about implementation.

## Prerequisites
`dotnet.dotnet` for DI/configuration/middleware fundamentals.

## Inputs Required
Whether the project uses minimal APIs or MVC controllers (match existing
convention — don't introduce the other style without reason), and the
authentication/authorization scheme already in place.

## Engineering Principles
1. Minimal APIs for small, focused endpoint sets; Controllers when you need
   filters, conventions, or a large, structured surface area — match
   whatever the project already uses.
2. Validate all input at the boundary (model validation / a validation
   library) before it reaches application/domain logic.
3. Return `ProblemDetails` for errors — consistent shape, not ad hoc error
   objects per endpoint.
4. Never bind directly to or return a domain entity — always a request/
   response DTO (`dotnet.api-design`).
5. Authorization is declared on the endpoint (`[Authorize]`/`RequireAuthorization`)
   with an explicit policy, not assumed from authentication alone.

## Step-by-Step Workflow
1. Define request/response DTOs for the endpoint.
2. Add validation (data annotations, FluentValidation, or manual checks) —
   fail fast with a 400 + `ProblemDetails` on invalid input.
3. Route to the application handler (command/query handler per
   `dotnet.architecture.cqrs`, or a service call) — the endpoint itself
   stays thin.
4. Map the handler's `Result`/outcome to the correct HTTP status
   (`dotnet.architecture.result-rop`).
5. Apply `RequireAuthorization("PolicyName")` explicitly; don't rely on a
   global default that might not fit this endpoint.
6. Add `CancellationToken` as a parameter, bound automatically from
   `HttpContext.RequestAborted` — propagate it through the call chain.

## Code Standards
- Minimal API handlers stay thin — parse/validate/delegate/map; business
  logic lives in the handler they call, not inline in the route delegate.
- Controllers use `[ApiController]` for automatic model validation and
  binding-source inference.
- Response DTOs never include fields the caller isn't authorized to see.

## Architecture Constraints
The endpoint layer depends on Application, never directly on Infrastructure
or Domain internals (`dotnet.architecture.clean-architecture`).

## Security Considerations
Every endpoint that isn't explicitly public has an authorization policy.
Validate all input server-side even if the client also validates — client
validation is UX, not a security boundary (`dotnet.security`).

## Testing Requirements
`WebApplicationFactory`-based integration tests covering: success case,
validation failure (400), unauthorized (401/403), and not-found (404) where
applicable (`dotnet.testing`).

## Common Mistakes
- Returning the EF Core entity directly from an endpoint — leaks internal
  shape and tracking state, and can over-expose fields.
- Skipping server-side validation because "the frontend already validates."
- Inconsistent error shapes across endpoints (some return
  `{ error: "..." }`, others `ProblemDetails`) — pick one, everywhere.

## Anti-Patterns
- **Fat endpoint**: business logic, data access, and mapping all inline in
  the route handler instead of delegated to an application handler.
- **Silent 200 on failure**: catching an exception and returning 200 with
  an error message in the body instead of the correct status code.

## Validation Checklist
- [ ] Input validated at the boundary; invalid input returns 400 +
      `ProblemDetails`.
- [ ] No domain entity returned directly; DTOs used both ways.
- [ ] Authorization policy explicit on protected endpoints.
- [ ] `CancellationToken` propagated.

## Definition of Done
Meets `rules/definition-of-done.md`; integration test covers success,
validation failure, and authorization failure.

## Example
```csharp
app.MapPost("/orders", async (
        CreateOrderRequest request,
        SubmitOrderHandler handler,
        CancellationToken ct) =>
    {
        if (request.Lines.Count == 0)
            return Results.ValidationProblem(new Dictionary<string, string[]>
            {
                ["lines"] = ["At least one line is required."]
            });

        var result = await handler.Handle(new SubmitOrderCommand(request.CustomerId, request.Lines), ct);

        return result.IsSuccess
            ? Results.Created($"/orders/{result.Value}", new { id = result.Value })
            : Results.Problem(detail: result.Error, statusCode: StatusCodes.Status400BadRequest);
    })
    .RequireAuthorization("CanCreateOrders")
    .WithName("CreateOrder");
```

## Related Skills
- `dotnet.api-design` — contract-level rules (versioning, pagination,
  idempotency).
- `dotnet.authentication` / `dotnet.authorization` — scheme and policy
  detail.
- `dotnet.testing` — `WebApplicationFactory` testing detail.
