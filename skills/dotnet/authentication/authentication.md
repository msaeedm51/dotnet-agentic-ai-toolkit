---
id: dotnet.authentication
title: Authentication (JWT, OAuth2, OIDC)
category: skill
domain: dotnet
technologies: [aspnetcore, jwt, oauth2, oidc]
triggers: [authentication, jwt, oauth2, oidc, login, token validation, identity provider]
requires: []
related: [dotnet.authorization, dotnet.security]
optional: []
prerequisites: []
tags: [security, authentication, jwt, oauth]
---

# Authentication (JWT, OAuth2, OIDC)

## Purpose
Verify who is calling the API correctly, using standard protocols (JWT
bearer tokens, OAuth2, OIDC) instead of a custom scheme, and configure
token validation so it can't be bypassed or confused.

## When to Use
Any endpoint that needs to know the caller's identity. Use an external
identity provider (Entra ID, Auth0, Keycloak, etc.) via OIDC/OAuth2 unless
there's a specific reason to issue tokens yourself.

## Prerequisites
None.

## Inputs Required
Which identity provider issues tokens, the expected issuer/audience, and
whether this service is a resource server only (validates tokens) or also
an OAuth2 client (initiates login flows).

## Engineering Principles
1. Prefer delegating authentication to a standards-based identity provider
   over rolling a custom login/token system.
2. Validate every claim that matters: issuer, audience, expiry, signature —
   never disable signature validation, even in development, without an
   explicit and temporary reason.
3. Tokens are short-lived; use refresh tokens (rotated, revocable) for
   long-lived sessions rather than long-lived access tokens.
4. Store tokens securely on the client side (httpOnly cookies or secure
   storage) — never in `localStorage` for anything sensitive if avoidable
   (XSS exposure).
5. Authentication proves identity; it does not by itself grant permission —
   that's `dotnet.authorization`.

## Step-by-Step Workflow
1. Register the JWT bearer authentication scheme with explicit
   `TokenValidationParameters`: validate issuer, audience, lifetime, and
   signing key.
2. Configure the identity provider's metadata endpoint (OIDC discovery) so
   signing keys rotate without a redeploy.
3. Map claims to `ClaimsPrincipal` in a way the rest of the app can use
   consistently (custom claim transformation if the provider's claim names
   don't match what authorization policies expect).
4. For a login/consent flow (this service as an OAuth2 client), use the
   provider's SDK/standard middleware rather than hand-rolling the
   authorization code flow.
5. Test token validation failure modes explicitly: expired, wrong audience,
   wrong issuer, tampered signature — each should be rejected with 401.

## Code Standards
`TokenValidationParameters` are explicit in code (or strongly-typed config),
not left at framework defaults, so validation behavior is visible and
reviewable.

## Architecture Constraints
Authentication configuration lives at the composition root
(`dotnet.dotnet`); business logic never inspects raw tokens — it works with
the resulting `ClaimsPrincipal`/`HttpContext.User`.

## Security Considerations
- Never accept an unsigned or "none" algorithm JWT.
- Validate audience — a token valid for a different API must be rejected
  here even if the issuer and signature are otherwise valid.
- Clock skew tolerance is small and explicit, not left unbounded.
- Refresh tokens are stored server-side/revocable, not just relied on
  client-side.

## Testing Requirements
Integration tests covering: valid token succeeds, expired token → 401,
wrong audience → 401, wrong issuer → 401, tampered signature → 401,
missing token on a protected endpoint → 401.

## Common Mistakes
- Trusting claims from the token without validating signature/issuer first.
- Long-lived access tokens used as a substitute for proper refresh-token
  rotation, increasing the exposure window if a token leaks.
- Rolling a custom username/password + token-issuance system instead of
  using an identity provider, absorbing security responsibilities (password
  storage, MFA, breach detection) the team likely isn't positioned to own.

## Anti-Patterns
- **Trust-on-parse**: reading claims out of a JWT payload without verifying
  the signature first (never do this — signature validation must happen
  before any claim is trusted).
- **God token**: cramming excessive data into the JWT payload instead of
  keeping it minimal and looking up detail server-side when needed.

## Validation Checklist
- [ ] Issuer, audience, lifetime, and signature are all validated.
- [ ] Expired/tampered/wrong-audience tokens are rejected with 401 and
      tested explicitly.
- [ ] Refresh tokens are rotated and revocable.
- [ ] No secret signing key or client secret committed to source.

## Definition of Done
Meets `rules/definition-of-done.md`; token validation failure modes are
covered by tests, not just the happy path.

## Example
```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Auth:Authority"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Auth:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Auth:Audience"],
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(2),
            ValidateIssuerSigningKey = true
        };
    });
```

## Related Skills
- `dotnet.authorization` — what an authenticated identity is allowed to do.
- `dotnet.security` — broader secrets/input-handling rules.
