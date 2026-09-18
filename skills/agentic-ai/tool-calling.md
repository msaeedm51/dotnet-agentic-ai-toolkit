---
id: agentic-ai.tool-calling
title: Tool Calling
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [tool calling, function calling, tool definition, tool schema, agent tools]
requires: [dotnet.api-design]
related: [agentic-ai.fundamentals.agent-loops, agentic-ai.structured-outputs, agentic-ai.ai-security]
optional: []
prerequisites: []
tags: [agents, tool-calling]
---

# Tool Calling

## Purpose
Define, expose, and execute tools an LLM can call — with schemas the model
can use reliably, and execution that enforces the same authorization and
validation a human-initiated call to the same operation would require.

## When to Use
The agent needs to take an action or fetch information beyond what's in its
prompt — call an API, query a database, run a calculation, search a
knowledge base.

## Prerequisites
None, but tools typically wrap existing application operations
(`dotnet.api-design`).

## Inputs Required
Which existing operations should be exposed as tools, and what
authorization context the agent is acting under (on behalf of a specific
user, or a system-level identity with its own scoped permissions).

## Engineering Principles
1. A tool's schema (name, description, parameters) is precise enough that
   the model can call it correctly without guessing — vague descriptions
   cause vague/wrong calls.
2. A tool wraps an existing, already-authorized application operation
   (`dotnet.architecture.clean-architecture` use case) — it doesn't bypass
   validation or authorization that would apply to the same operation
   called any other way.
3. Tool execution has its own timeout and error handling, independent of
   the overall agent loop bound.
4. Tool results returned to the model are the minimum necessary
   information, not a raw dump of an entire object graph
   (`agentic-ai.context-engineering`).
5. A failed tool call returns a structured error the model can reason about
   ("order not found," not a raw stack trace) — never leak internal
   exception detail into the model's context (`dotnet.security`).

## Step-by-Step Workflow
1. Identify the existing application operation the tool should wrap.
2. Write the tool schema: name, clear description of when/how to use it,
   and a strongly-typed parameter schema.
3. Implement the tool handler calling the existing application
   service/handler — same authorization checks as any other caller.
4. Wrap execution with its own timeout; catch exceptions and translate them
   to a structured, model-safe error result.
5. Register the tool with the agent's tool registry, scoped to the agents/
   contexts actually authorized to use it (`agentic-ai.fundamentals.multi-agent-systems`
   — not every agent needs every tool).
6. Add an evaluation case asserting the model calls this tool correctly for
   a representative task.

## Code Standards
Tool parameter types are strongly-typed records deserialized from the
model's structured tool-call arguments — not manually parsed from a raw
string.

## Architecture Constraints
A tool handler is a thin adapter calling into the existing application
layer — it does not contain new business logic that only exists for the
agent's benefit and bypasses the same rules a human-facing endpoint would
enforce.

## Security Considerations
- Every tool call is authorized in the actual current context — an agent
  acting "on behalf of" a user must not be able to call a tool that user
  couldn't call themselves, unless deliberately designed as a
  system-level capability with its own justification.
- Tool descriptions and parameter schemas are not a place to embed
  instructions the agent should blindly trust from tool *output* — the
  description guides the model on how to call the tool; the tool's
  *result*, especially if it includes external/user-controlled content,
  is untrusted data (`agentic-ai.ai-security`).
- Irreversible tools (send, pay, delete, publish) require a
  human-in-the-loop checkpoint (`agentic-ai.human-in-the-loop`).

## Testing Requirements
Unit test each tool handler directly (authorization enforced, errors
translated safely). Evaluation-test that the model selects and calls the
right tool with correct arguments for representative tasks.

## Common Mistakes
- A tool that bypasses the authorization checks the equivalent human-facing
  operation has, because "it's just for the agent."
- Returning a full entity/exception detail as the tool result instead of a
  minimal, safe summary.
- A tool description vague enough that the model calls it with the wrong
  arguments or in the wrong situation.

## Anti-Patterns
- **God tool**: one tool with a dozen optional parameters doing many
  different things, instead of several focused tools with clear, narrow
  purposes — the model calls a focused tool more reliably.
- **Unbounded search tool**: a "search everything" tool with no result
  limit, capable of returning an enormous payload into context.

## Validation Checklist
- [ ] Tool schema is precise; description states when/how to use it.
- [ ] Tool execution enforces the same authorization as any other caller
      of the underlying operation.
- [ ] Tool results are minimal and don't leak internal exception detail.
- [ ] Irreversible tools require human-in-the-loop.
- [ ] Evaluation case exists for correct tool selection/arguments.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; the tool has
both a unit test (handler correctness) and an evaluation case (model
selects/calls it correctly).

## Example
```csharp
public sealed record GetOrderStatusArgs(Guid OrderId);

public sealed class GetOrderStatusTool(IOrderRepository repository) : IAgentTool<GetOrderStatusArgs>
{
    public ToolDefinition Definition => new(
        Name: "get_order_status",
        Description: "Look up the current status of an order by its id.",
        ParameterSchema: JsonSchema.From<GetOrderStatusArgs>());

    public async Task<ToolResult> ExecuteAsync(GetOrderStatusArgs args, AgentContext ctx, CancellationToken ct)
    {
        var order = await repository.FindAsync(new OrderId(args.OrderId), ct);
        if (order is null || order.CustomerId != ctx.OnBehalfOfUserId)
            return ToolResult.SafeError("Order not found."); // no internal detail leaked

        return ToolResult.Success(new { status = order.Status.ToString() });
    }
}
```

## Related Skills
- `agentic-ai.fundamentals.agent-loops` — where tool calls happen.
- `agentic-ai.structured-outputs` — schema-driven argument parsing.
- `agentic-ai.ai-security` — trust boundary for tool output.
