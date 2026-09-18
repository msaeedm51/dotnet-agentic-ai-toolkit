---
id: dotnet.messaging
title: Messaging (Queues, Brokers, Delivery Guarantees)
category: skill
domain: dotnet
technologies: [dotnet, rabbitmq, azureservicebus, kafka]
triggers: [message queue, service bus, rabbitmq, kafka, at least once delivery, message broker]
requires: []
related: [dotnet.architecture.event-driven, dotnet.architecture.domain-events-outbox, dotnet.architecture.background-processing]
optional: []
prerequisites: [dotnet.architecture.event-driven]
tags: [messaging, queues]
---

# Messaging (Queues, Brokers, Delivery Guarantees)

## Purpose
Send and consume messages reliably across process/service boundaries, with
delivery guarantees and consumer idempotency designed deliberately rather
than assumed.

## When to Use
Publishing/consuming integration events (`dotnet.architecture.event-driven`),
decoupled cross-service communication, or work queue processing. Not for
in-process communication, which doesn't need a broker.

## Prerequisites
`dotnet.architecture.event-driven`.

## Inputs Required
The broker already in use or chosen for the project (Azure Service Bus,
RabbitMQ, Kafka), and the delivery guarantee the consumer actually needs.

## Engineering Principles
1. Most brokers guarantee at-least-once delivery — design every consumer to
   be idempotent (processing the same message twice has the same effect as
   once).
2. Ordering is not guaranteed across partitions/consumers by default in
   most brokers — don't depend on message order unless the broker/topology
   explicitly guarantees it (e.g. a single partition key).
3. Dead-letter failed messages after a bounded retry count — don't retry
   forever, and don't silently drop a message that can't be processed.
4. Publish reliably via the outbox pattern
   (`dotnet.architecture.domain-events-outbox`) rather than publishing
   directly inside the business transaction.
5. Consumers run as background services (`dotnet.architecture.background-processing`),
   with per-message failure isolation — one bad message doesn't stop the
   whole consumer.

## Step-by-Step Workflow
1. Confirm the broker and topology already used by the project (queue vs.
   topic/pub-sub, partitioning strategy).
2. Design the message schema, versioned if consumers may be deployed
   independently.
3. Publish via the outbox, not directly from the request handler.
4. Implement the consumer as a background service, processing each message
   with try/catch, dead-lettering after a bounded retry count.
5. Make the consumer idempotent — check a processed-message log/dedupe key,
   or design the operation itself to be naturally idempotent (an upsert
   instead of an insert).
6. Add observability: consumer lag, dead-letter queue depth, processing
   failures — these are the metrics that reveal a stuck pipeline.

## Code Standards
Message contracts are versioned types in a shared (or published) schema
location consumers can reference without depending on the producer's
internal code.

## Architecture Constraints
A consumer never assumes the producer's internal implementation — only the
published message contract. Producers don't know or care who consumes a
message (`dotnet.architecture.event-driven`).

## Security Considerations
Message payloads crossing a trust boundary follow the same data-exposure
rules as any other cross-boundary contract; broker credentials are
least-privilege and never hardcoded.

## Testing Requirements
Integration tests against a real broker (Testcontainers where available,
or the broker's local emulator) for publish/consume round-trip and
dead-letter behavior; unit tests for consumer idempotency (processing the
same message twice produces the same end state).

## Common Mistakes
- Assuming exactly-once delivery from a broker that only guarantees
  at-least-once, causing duplicate side effects (double-charging, double-
  sending an email) on redelivery.
- Retrying a poison message forever instead of dead-lettering it after a
  bounded count, blocking the whole queue behind it.
- Publishing directly inside the request transaction without an outbox,
  losing the event if the process crashes between commit and publish.

## Anti-Patterns
- **Assumed ordering**: logic that breaks if two related messages arrive
  out of order, with no explicit ordering guarantee from the broker/
  topology backing that assumption.
- **Fat consumer**: one consumer handling many unrelated message types with
  a large branching dispatch, instead of focused consumers per message
  type/concern.

## Validation Checklist
- [ ] Consumers are idempotent against redelivery.
- [ ] Poison messages are dead-lettered after a bounded retry count, not
      retried forever.
- [ ] Publishing goes through the outbox, not directly in the request path.
- [ ] Message schema is versioned if consumers deploy independently.

## Definition of Done
Meets `rules/definition-of-done.md`; consumer idempotency and dead-letter
behavior are covered by tests.

## Example
```csharp
public sealed class OrderPlacedConsumer(IProcessedMessageStore dedupe, IInventoryService inventory)
{
    public async Task HandleAsync(OrderPlacedMessage message, CancellationToken ct)
    {
        if (await dedupe.WasProcessedAsync(message.MessageId, ct))
            return; // idempotent: safe to process the same message twice

        await inventory.ReserveStockAsync(message.OrderId, message.Lines, ct);
        await dedupe.MarkProcessedAsync(message.MessageId, ct);
    }
}
```

## Related Skills
- `dotnet.architecture.event-driven` — event design this messaging layer
  transports.
- `dotnet.architecture.domain-events-outbox` — reliable publish mechanism.
- `dotnet.architecture.background-processing` — consumer hosting pattern.
