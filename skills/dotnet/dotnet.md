---
id: dotnet.dotnet
title: .NET Runtime & Hosting Fundamentals
category: skill
domain: dotnet
technologies: [dotnet8, dotnet9, aspnetcore]
triggers: [dependency injection, configuration, options pattern, middleware, logging, opentelemetry, health checks, httpclientfactory, resilience, rate limiting, output caching]
requires: [dotnet.csharp]
related: [dotnet.aspnetcore, dotnet.caching, dotnet.performance, dotnet.architecture.background-processing]
optional: []
prerequisites: [dotnet.csharp]
tags: [dotnet, hosting, di, observability]
---

# .NET Runtime & Hosting Fundamentals

## Purpose
Cover the cross-cutting .NET 8+ hosting concerns every service needs
regardless of whether it's an API, worker, or CLI: dependency injection,
configuration, middleware, logging/observability, health checks, resilient
outbound HTTP, and rate limiting.

## When to Use
Any project using the generic host (`WebApplication`/`IHost`) — essentially
every ASP.NET Core or worker-service project.

## Prerequisites
`dotnet.csharp`.

## Inputs Required
Whether the project is a web API, worker service, or both, and what
external dependencies it calls out to (for resilience/health check design).

## Engineering Principles
1. Register services with the narrowest correct lifetime: `Singleton` for
   stateless/thread-safe, `Scoped` for per-request/per-unit-of-work,
   `Transient` for lightweight stateless.
2. Configuration is strongly typed via the Options pattern
   (`IOptions<T>`/`IOptionsSnapshot<T>`), not scattered
   `IConfiguration["Key:SubKey"]` string lookups through the codebase.
3. Middleware order matters and is deliberate: exception handling →
   HTTPS redirection → routing → authentication → authorization → endpoints.
4. Every outbound HTTP call goes through `HttpClientFactory` with an
   explicit resilience policy (timeout, retry, circuit breaker) — never
   `new HttpClient()` per call (socket exhaustion) or unbounded retries.
5. Structured logging (not string concatenation) with correlation
   IDs/trace context flowing through, via `ILogger<T>` and OpenTelemetry.
6. Health checks distinguish liveness (is the process alive) from readiness
   (can it serve traffic — e.g. database reachable).

## Step-by-Step Workflow
1. Register configuration via `services.Configure<TOptions>(config.GetSection("..."))`
   and inject `IOptions<TOptions>` (or `IOptionsSnapshot<TOptions>` if it
   must reload without a restart).
2. Register services with explicit lifetimes; validate scoped-in-singleton
   mistakes don't slip through (`ValidateScopes = true` in development).
3. Build the middleware pipeline in the correct order; add exception
   handling middleware first so it wraps everything downstream.
4. Register `HttpClientFactory` typed clients with
   `AddStandardResilienceHandler()` (or explicit Polly policies) for every
   outbound dependency.
5. Wire OpenTelemetry (traces, metrics, logs) and health checks
   (`/health/live`, `/health/ready`) before shipping to any environment
   that isn't local dev.
6. Apply rate limiting (`Microsoft.AspNetCore.RateLimiting`) to endpoints
   that are expensive or abusable.

## Code Standards
- No `IConfiguration` injected directly into business logic — bind to a
  typed options class at the composition root.
- `HttpClient` instances always come from `IHttpClientFactory`, never
  constructed directly for repeated use.
- Log messages use structured parameters (`logger.LogInformation("Order {OrderId} submitted", id)`),
  never string interpolation into the message template.

## Architecture Constraints
Composition root (`Program.cs`) is the only place that wires every layer
together; business logic never resolves services from `IServiceProvider`
directly (service locator anti-pattern) — dependencies are injected.

## Security Considerations
Secrets never live in `appsettings.json` committed to source — use user
secrets locally, environment variables/managed identity/Key Vault in
deployed environments (`rules/security.md`). Logs never include secrets,
tokens, or full PII payloads.

## Testing Requirements
Integration-test the composition root with `WebApplicationFactory`
(`dotnet.testing`) to catch DI misconfiguration (a missing registration
fails at startup, which should be caught by a test, not first discovered in
production).

## Common Mistakes
- Injecting `IConfiguration` everywhere instead of typed options — makes
  config keys untyped strings scattered across the codebase.
- Registering a `DbContext` (scoped) as a dependency of a singleton service
  — throws at runtime or causes a captured, stale instance.
- `new HttpClient()` per request — exhausts sockets under load
  (`dotnet.performance`).

## Anti-Patterns
- **Service locator**: resolving dependencies from `IServiceProvider`
  inside business logic instead of constructor injection.
- **God `Program.cs`**: all configuration, middleware, and business wiring
  in one unstructured file with no extension methods grouping related
  registrations.

## Validation Checklist
- [ ] Configuration is strongly typed via Options pattern.
- [ ] Outbound HTTP goes through `HttpClientFactory` with a resilience
      policy.
- [ ] Health checks separate liveness from readiness.
- [ ] No scoped service injected into a singleton.
- [ ] Structured logging used throughout, no secrets logged.

## Definition of Done
Meets `rules/definition-of-done.md`; DI registrations verified by an
integration test that boots the host.

## Example
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<PaymentOptions>(builder.Configuration.GetSection("Payment"));

builder.Services.AddHttpClient<IPaymentClient, PaymentClient>(c =>
        c.Timeout = TimeSpan.FromSeconds(10))
    .AddStandardResilienceHandler();

builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: ["live"])
    .AddDbContextCheck<AppDbContext>("database", tags: ["ready"]);

builder.Services.AddOpenTelemetry()
    .WithTracing(t => t.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation());

var app = builder.Build();
app.UseExceptionHandler();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = c => c.Tags.Contains("live") });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = c => c.Tags.Contains("ready") });
app.MapControllers();
app.Run();
```

## Related Skills
- `dotnet.aspnetcore` — HTTP-API-specific concerns built on this foundation.
- `dotnet.caching` — output/distributed caching detail.
- `dotnet.architecture.background-processing` — `BackgroundService` hosting.
