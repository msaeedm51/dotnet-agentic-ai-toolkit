---
id: rule.dotnet
title: .NET Runtime Rules
category: rule
tech_tags: [dotnet, aspnetcore]
triggers: [dotnet rules, di lifetime rule, httpclientfactory rule, configuration rule]
severity: blocking
tags: [dotnet]
---

# .NET Runtime Rules

## Use the narrowest correct DI lifetime

**Rule:** Services are registered `Scoped` unless they're genuinely
stateless/thread-safe (`Singleton`) or lightweight and stateless
(`Transient`) — never `Singleton` by default for convenience.

**Why:** A scoped dependency (like `DbContext`) injected into a singleton
either throws or captures a stale instance for the app's lifetime.

**Applies to:** Every DI registration.

**Exception:** None — the lifetime is determined by the service's actual
statefulness, not convenience.

---

## Configuration is strongly typed

**Rule:** Configuration is bound to a typed options class
(`IOptions<T>`/`IOptionsSnapshot<T>`) at the composition root; business
logic never reads `IConfiguration["Key:SubKey"]` directly.

**Why:** Untyped configuration access scatters magic strings through the
codebase and loses compile-time safety.

**Applies to:** All configuration access outside the composition root.

**Exception:** None.

---

## Outbound HTTP goes through `HttpClientFactory`

**Rule:** No `new HttpClient()` for repeated use; every outbound HTTP
dependency is registered via `AddHttpClient` with an explicit resilience
policy.

**Why:** Manually constructed `HttpClient` instances exhaust sockets under
load; `HttpClientFactory` manages the underlying handler lifetime
correctly.

**Applies to:** Every outbound HTTP call.

**Exception:** A single, short-lived `HttpClient` instance in a test or
script context with no production traffic.

---

## No secret in source or committed configuration

**Rule:** Secrets (connection strings with credentials, API keys) never
appear in source control — use user secrets locally, environment
variables/Key Vault/managed identity in deployed environments.

**Why:** A secret in git history persists even after it's later removed
from the working tree — rotation is required, not just removal.

**Applies to:** Every secret.

**Exception:** None.

---

## Structured logging, never string interpolation into the message template

**Rule:** `ILogger` calls use structured parameters
(`LogInformation("Order {OrderId} submitted", id)`), never
`LogInformation($"Order {id} submitted")`.

**Why:** Structured parameters remain queryable in log aggregation;
interpolated strings collapse everything to unstructured text.

**Applies to:** Every log call.

**Exception:** None.

---

## Never log secrets, tokens, or full PII payloads

**Rule:** Log statements never include a password, token, API key, or an
entire request/response body known to contain PII.

**Why:** Logs are frequently less access-controlled and longer-retained
than the primary datastore, making them a common compliance and breach
exposure point.

**Applies to:** Every log call.

**Exception:** None.

---

## Health checks distinguish liveness from readiness

**Rule:** A liveness check (`/health/live`) answers "is the process alive";
a readiness check (`/health/ready`) answers "can it serve traffic" (e.g.
database reachable) — they are not the same check.

**Why:** Conflating them causes an orchestrator to restart a healthy
process during a transient dependency outage, or to keep routing traffic to
an instance that can't actually serve it.

**Applies to:** Any service with orchestrator-managed health checks.

**Exception:** A single-process local-only tool with no orchestrator.
