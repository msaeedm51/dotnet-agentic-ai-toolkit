---
id: dotnet.security
title: Application Security (OWASP-Oriented)
category: skill
domain: dotnet
technologies: [aspnetcore, dotnet]
triggers: [security review, owasp, sql injection, xss, csrf, ssrf, secrets, sensitive data, security headers]
requires: []
related: [dotnet.authentication, dotnet.authorization, dotnet.api-design]
optional: []
prerequisites: []
tags: [security, owasp]
---

# Application Security (OWASP-Oriented)

## Purpose
Prevent the concrete, recurring classes of vulnerability in .NET web
applications — not a list to recite, but specific checks and .NET
mechanisms to apply them with.

## When to Use
Any change touching input handling, output rendering, data access,
file handling, external requests, or secrets. Escalate non-trivial findings
to `agent.security-reviewer`.

## Prerequisites
None.

## Inputs Required
What untrusted input the change accepts (user input, external API
responses, file uploads) and where it flows.

## Engineering Principles
1. Validate all untrusted input at the boundary; never trust client-side
   validation alone.
2. Parameterize every database query — never string-concatenate user input
   into SQL (`dotnet.efcore` covers the EF Core-specific version of this).
3. Encode output for its context (HTML, JSON, URL) — never trust a
   framework's default is enough without checking the actual template/
   serialization path.
4. Secrets live in a secret store (user secrets locally, Key Vault/managed
   identity in production) — never in source control or `appsettings.json`.
5. Least privilege everywhere: database accounts, service identities, API
   scopes.
6. Log security-relevant events (auth failures, authorization denials)
   without logging the secrets/tokens/PII involved.

## Step-by-Step Workflow
1. Identify every point untrusted input enters the change (request body,
   query string, headers, file upload, external API response).
2. Validate type, range, and format at the boundary; reject early with a
   clear error, don't silently coerce.
3. For anything reaching a database: confirm it's parameterized (EF Core
   LINQ, or `FromSqlInterpolated`/parameterized raw SQL — never
   `FromSqlRaw` with interpolated strings).
4. For anything reaching a browser: confirm the output context is encoded
   correctly (Razor auto-encodes HTML by default — verify `Html.Raw`/
   `[AllowHtml]` aren't used on untrusted content).
5. For anything triggering an outbound request based on user input
   (webhooks, URL fetch): validate/allowlist the target to prevent SSRF —
   never fetch an arbitrary user-supplied URL from server-side code without
   restriction.
6. For file uploads: validate content type by inspection (not just the
   extension/declared MIME type), enforce size limits, store outside the
   web root or in blob storage, never execute uploaded content.
7. Add/verify security headers (`Content-Security-Policy`,
   `X-Content-Type-Options`, `Strict-Transport-Security`) at the middleware
   level for anything serving browser content.

## Code Standards
No raw SQL string concatenation. No `Html.Raw` on untrusted content. No
secret literal in source, config committed to git, or log statement.

## Architecture Constraints
Security-relevant validation happens at the boundary (API layer), not only
deep in the domain — but domain invariants (`dotnet.architecture.ddd`)
still provide defense in depth if the boundary check is ever bypassed by a
new caller.

## Security Considerations
This skill *is* the security considerations section for other skills —
cross-reference here rather than restating.

- **SQL injection**: parameterized queries only.
- **XSS**: context-aware output encoding; CSP as defense in depth.
- **CSRF**: anti-forgery tokens for cookie-authenticated state-changing
  requests (less relevant for pure bearer-token APIs, but confirm the
  auth model before assuming it doesn't apply).
- **SSRF**: allowlist outbound targets derived from user input.
- **Insecure deserialization**: never deserialize untrusted data with a
  binder that allows arbitrary type resolution.
- **Sensitive data exposure**: encrypt at rest where required, TLS in
  transit always, minimal data in logs/error messages.
- **Path traversal**: never build a file path by concatenating user input;
  validate/normalize and confirm it stays within the intended directory.

## Testing Requirements
A security-relevant fix gets a test proving the vulnerable input is now
rejected/handled safely, not just a manual check.

## Common Mistakes
- Assuming EF Core LINQ is automatically safe but then dropping to
  `FromSqlRaw($"...")` for a "quick" query — reintroduces injection risk.
- Logging the full request body on error for debugging convenience,
  including passwords/tokens in it.
- Validating file upload type by extension only, allowing a renamed
  executable through.

## Anti-Patterns
- **Security theater**: adding a security header or a validation check that
  doesn't address the actual threat model, to appear compliant.
- **Trust the framework blindly**: assuming a framework default (e.g. Razor
  encoding) applies everywhere without checking the specific code path
  (`Html.Raw`, custom serialization, non-Razor output).

## Validation Checklist
- [ ] All untrusted input validated at the boundary.
- [ ] No string-concatenated SQL.
- [ ] Output encoded for its context; no unreviewed `Html.Raw`.
- [ ] No secret in source, config, or logs.
- [ ] Outbound requests from user input are allowlisted (SSRF).
- [ ] File uploads validated by content, size-limited, stored safely.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/security.md`; a security-
relevant change has `agent.security-reviewer` sign-off.

## Example
```csharp
// SSRF-safe outbound fetch: allowlist, not arbitrary user URL
public async Task<Result<Stream>> FetchAllowedResourceAsync(Uri requested, CancellationToken ct)
{
    if (!_allowedHosts.Contains(requested.Host))
        return Result<Stream>.Failure("Host is not allowed.");

    var response = await _httpClient.GetAsync(requested, ct);
    return response.IsSuccessStatusCode
        ? Result<Stream>.Success(await response.Content.ReadAsStreamAsync(ct))
        : Result<Stream>.Failure($"Upstream returned {response.StatusCode}.");
}
```

## Related Skills
- `dotnet.authentication` / `dotnet.authorization` — identity and
  permission enforcement.
- `dotnet.api-design` — where validation failures surface in the contract.
- `agentic-ai.ai-security` — the agentic-AI-specific extension of this
  skill (prompt injection, tool-output trust).
