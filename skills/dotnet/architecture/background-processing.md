---
id: dotnet.architecture.background-processing
title: Background Processing
category: skill
domain: dotnet
technologies: [dotnet, aspnetcore]
triggers: [background service, hosted service, background job, scheduled task, worker]
requires: []
related: [dotnet.dotnet, dotnet.architecture.domain-events-outbox, dotnet.performance]
optional: []
prerequisites: []
tags: [architecture, background-jobs]
---

# Background Processing

## Purpose
Run work outside the HTTP request/response cycle correctly: long-running
tasks, scheduled jobs, queue consumers, and outbox publishers — with proper
lifecycle management, error handling, and shutdown behavior.

## When to Use
- Work that shouldn't block a request (email sending, report generation).
- Polling/consuming a queue or outbox table.
- Scheduled/periodic tasks.
- Not for work the caller needs a synchronous result from — that's a normal
  request handler, not a background service.

## Prerequisites
`dotnet.dotnet` for hosting/DI fundamentals.

## Inputs Required
Whether the work must survive a process restart (needs persisted state/
checkpointing) or can be safely lost and retried.

## Engineering Principles
1. Use `BackgroundService`/`IHostedService` for anything that runs for the
   life of the application, not a fire-and-forget `Task.Run` from a request
   handler (which isn't tracked by the host and can be silently killed on
   shutdown).
2. Respect `CancellationToken` from `ExecuteAsync` throughout — a background
   service that ignores it can't shut down cleanly, delaying deploys.
3. Every iteration/job handles its own failure — one failed item must not
   crash the loop and take down all future processing.
4. Idempotency matters more here than almost anywhere — a background job
   will eventually run twice (restart mid-work, at-least-once queue
   delivery); design for that from the start.
5. Scoped services (like `DbContext`) must be resolved from a new
   `IServiceScope` per unit of work inside a singleton `BackgroundService`
   — not injected directly into the constructor.

## Step-by-Step Workflow
1. Implement `BackgroundService`, injecting `IServiceScopeFactory` (not
   scoped services directly, since the service itself is a singleton).
2. In `ExecuteAsync`, loop with the provided `stoppingToken`, creating a new
   scope per unit of work.
3. Wrap each unit of work in try/catch — log and continue (or apply a
   backoff/retry policy) rather than letting one failure kill the loop.
4. Use `PeriodicTimer` for interval-based polling instead of
   `Task.Delay`-in-a-loop (cleaner cancellation semantics).
5. Handle graceful shutdown: `StopAsync` should let in-flight work finish
   within a bounded time, not abandon it instantly.

## Code Standards
Background services are registered via `AddHostedService<T>()`; they never
reach into `HttpContext` or anything request-scoped.

## Architecture Constraints
A `BackgroundService` is a singleton for its own lifetime, but must resolve
scoped dependencies (`DbContext`, scoped repositories) through a new scope
per work item — sharing one scope across the service's entire lifetime
causes stale/leaked `DbContext` issues.

## Security Considerations
Background jobs often run with elevated/system-level credentials (no user
context) — be deliberate about what data they can touch; don't assume the
same authorization checks that apply to a user-initiated request are
redundant here.

## Testing Requirements
Unit test the per-item processing logic directly (extract it from the
`ExecuteAsync` loop so it's testable without hosting infrastructure).
Integration-test the full loop against a real or test queue/outbox for
timing and cancellation behavior.

## Common Mistakes
- Using `Task.Run` from a controller/endpoint to "run something in the
  background" — not tracked by the host, silently lost on app shutdown or
  scale-down.
- Injecting a scoped `DbContext` directly into a singleton
  `BackgroundService` constructor — throws or causes subtle bugs.
- Letting one exception in the processing loop crash the entire service.

## Anti-Patterns
- **Fire-and-forget from a request**: `_ = DoWorkAsync()` in a controller
  action — no error handling, no shutdown coordination, invisible to the
  host's lifecycle.
- **Unbounded retry with no backoff**: a poison message retried in a tight
  loop, consuming CPU and flooding logs.

## Validation Checklist
- [ ] Uses `BackgroundService`/`IHostedService`, not `Task.Run` from a
      request handler.
- [ ] Scoped dependencies resolved via a new scope per unit of work.
- [ ] One item's failure doesn't stop processing of subsequent items.
- [ ] `CancellationToken` respected for graceful shutdown.

## Definition of Done
Meets `rules/definition-of-done.md`; the processing logic is unit-tested
independent of the hosting loop; graceful shutdown behavior is verified.

## Example
```csharp
public sealed class OutboxPublisherService(
    IServiceScopeFactory scopeFactory,
    ILogger<OutboxPublisherService> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(5));
        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            using var scope = scopeFactory.CreateScope();
            var publisher = scope.ServiceProvider.GetRequiredService<IOutboxPublisher>();

            try
            {
                await publisher.PublishPendingAsync(stoppingToken);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogError(ex, "Outbox publish cycle failed; will retry next tick.");
            }
        }
    }
}
```

## Related Skills
- `dotnet.dotnet` — hosting/DI fundamentals this relies on.
- `dotnet.architecture.domain-events-outbox` — the most common consumer of
  this pattern.
- `dotnet.performance` — throughput/backpressure considerations under load.
