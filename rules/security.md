---
id: rule.security
title: Security Rules
category: rule
tech_tags: [aspnetcore, dotnet]
triggers: [security rules, owasp rules, secrets rule, least privilege rule]
severity: blocking
tags: [security]
---

# Security Rules

## Never hard-code secrets

**Rule:** No password, API key, connection string credential, or signing
key appears as a literal in source code or a committed configuration file.

**Why:** A committed secret persists in git history even after later
removal — rotation, not deletion, is the only real fix once it's happened.

**Applies to:** Every secret.

**Exception:** None.

---

## Never log passwords or tokens

**Rule:** No log statement includes a password, bearer token, API key, or
session identifier in a form that could be used to impersonate the
subject.

**Why:** Logs are frequently less access-controlled and longer-retained
than primary data stores.

**Applies to:** Every log call.

**Exception:** None.

---

## Validate untrusted input

**Rule:** Every value originating outside this codebase's direct control
(request body, query string, header, file upload, external API response)
is validated before use — type, range, format, and, for file uploads,
actual content.

**Why:** Unvalidated input is the root cause behind most of the OWASP
Top 10 categories.

**Applies to:** Every untrusted input source.

**Exception:** None.

---

## Apply least privilege

**Rule:** A database account, service identity, or API scope has exactly
the access it needs — not broader "to be safe" or for convenience.

**Why:** Excess privilege turns a contained bug or compromise into a much
larger blast radius.

**Applies to:** Every credential/identity/role assignment.

**Exception:** None.

---

## Explicitly authorize sensitive operations

**Rule:** An operation with real consequence (data modification, financial
action, privileged read) has an explicit authorization check at its
enforcement boundary — never inferred from authentication alone or from
client-side UI state.

**Why:** A missing explicit check is exploitable the moment someone calls
the operation directly instead of through the intended UI path.

**Applies to:** Every sensitive operation.

**Exception:** None.

---

## Parameterize every database query

**Rule:** No SQL is built by string-concatenating untrusted input — always
parameterized queries or an ORM's parameterized query mechanism.

**Why:** This is the direct, mechanical prevention of SQL injection.

**Applies to:** Every database query.

**Exception:** None.

---

## Encode output for its context

**Rule:** Content rendered into HTML, inserted into a URL, or embedded in
another format is encoded for that specific context — never trusted as
"probably safe" because a framework usually handles it.

**Why:** Cross-site scripting comes from exactly the gap between "usually
encoded" and "explicitly encoded for this specific output context."

**Applies to:** Any untrusted content rendered to a browser or another
interpreter.

**Exception:** None.

---

## Allowlist outbound requests derived from user input

**Rule:** A server-side request whose target is influenced by user input
(a webhook URL, a "fetch this link" feature) is validated against an
allowlist before the request is made.

**Why:** An unrestricted server-side fetch of a user-supplied URL is the
direct mechanism of a server-side request forgery (SSRF) attack.

**Applies to:** Any outbound request with a user-influenced target.

**Exception:** None.
