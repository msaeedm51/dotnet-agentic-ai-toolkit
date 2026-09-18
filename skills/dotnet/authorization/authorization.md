---
id: dotnet.authorization
title: Authorization (Policy & Resource-Based)
category: skill
domain: dotnet
technologies: [aspnetcore]
triggers: [authorization, policy based authorization, resource based authorization, roles, claims, permissions]
requires: []
related: [dotnet.authentication, dotnet.security, dotnet.api-design]
optional: []
prerequisites: [dotnet.authentication]
tags: [security, authorization]
---

# Authorization (Policy & Resource-Based)

## Purpose
Decide what an authenticated identity is allowed to do, enforced
consistently at the correct boundary — never inferred from the UI, and
never skipped because "the user is already logged in."

## When to Use
Any endpoint or operation where different authenticated users should be
allowed different things.

## Prerequisites
`dotnet.authentication` — authorization needs a trustworthy identity first.

## Inputs Required
The actual authorization model: role-based, claims-based, or resource-based
(does the user own/have access to *this specific* resource, not just have a
role that generally allows the operation).

## Engineering Principles
1. Authorization is enforced server-side, at the boundary the request
   actually crosses (endpoint or application handler) — never assumed from
   client-side UI hiding a button.
2. Policy-based authorization (named policies with explicit requirements)
   over scattered `if (user.IsInRole(...))` checks duplicated across
   endpoints.
3. Resource-based authorization for "can this user act on this specific
   resource" (not just "does this user have this role") — role alone is
   often insufficient (e.g. "can edit orders" vs. "can edit *this*
   customer's* orders").
4. Deny by default — an endpoint with no explicit policy should not be
   silently open; confirm what the project's default is and make it
   explicit.
5. Least privilege — a policy grants exactly what's needed, not a broader
   role that happens to include it.

## Step-by-Step Workflow
1. Identify the authorization model needed: role check, claim check, or
   resource-based ownership check.
2. Define a named policy (`AddAuthorization(options => options.AddPolicy(...))`)
   rather than inline role checks.
3. For resource-based checks, implement `IAuthorizationHandler` that loads
   the resource and checks the specific relationship (ownership, tenant,
   assignment) — don't approximate it with a role alone.
4. Apply the policy explicitly on the endpoint/action
   (`RequireAuthorization("PolicyName")`).
5. Test both the allowed and denied case for every policy.

## Code Standards
Policy names are descriptive of the capability (`CanCancelOwnOrders`), not
generic (`Policy1`). Authorization handlers are small, single-purpose, and
testable independent of HTTP.

## Architecture Constraints
Authorization logic lives in a dedicated handler/policy, not duplicated
inline across multiple endpoints that need the same check.

## Security Considerations
- A missing authorization check is a BLOCKER-severity finding
  (`agents/security-reviewer.md`), not a style note.
- Don't conflate "authenticated" with "authorized" — a valid token proves
  identity, not permission.
- Multi-tenant systems: every resource-based check must include tenant
  isolation, not just resource ownership within a tenant.

## Testing Requirements
For every policy: a test proving the allowed case succeeds and a test
proving the denied case returns 403 (not 200, not 500, not silently
succeeding).

## Common Mistakes
- Checking authorization in the UI/frontend only, trusting the API to be
  safe because "no one would call it directly" — it will be called
  directly, by someone.
- Role-only checks where the real requirement is resource ownership (any
  "Editor" can edit any order, not just their own).
- Forgetting authorization on a newly added endpoint because the policy
  wasn't part of the template/scaffolding used to create it.

## Anti-Patterns
- **Scattered role checks**: `if (User.IsInRole("Admin"))` duplicated
  across a dozen endpoints instead of one named policy.
- **Client-side-only enforcement**: hiding a UI element without a
  corresponding server-side check.

## Validation Checklist
- [ ] Every non-public endpoint has an explicit authorization policy.
- [ ] Resource-based checks verify ownership/tenant, not just role.
- [ ] Both allow and deny cases are tested for each policy.

## Definition of Done
Meets `rules/definition-of-done.md`; every new/changed endpoint's
authorization is covered by an allow-case and a deny-case test.

## Example
```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("CanCancelOwnOrders", policy =>
        policy.Requirements.Add(new OwnsResourceRequirement()));
});

public sealed class OwnsResourceHandler(IOrderRepository repository)
    : AuthorizationHandler<OwnsResourceRequirement, OrderId>
{
    protected override async Task HandleRequirementAsync(
        AuthorizationHandlerContext context, OwnsResourceRequirement requirement, OrderId resource)
    {
        var order = await repository.FindAsync(resource, CancellationToken.None);
        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);

        if (order is not null && order.CustomerId.ToString() == userId)
            context.Succeed(requirement);
    }
}
```

## Related Skills
- `dotnet.authentication` — establishing the identity this authorizes.
- `dotnet.security` — broader OWASP-class rules.
- `dotnet.api-design` — where authorization failures map to 401 vs. 403.
