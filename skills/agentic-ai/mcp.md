---
id: agentic-ai.mcp
title: MCP (Model Context Protocol)
category: skill
domain: agentic-ai
technologies: [dotnet, mcp]
triggers: [mcp, model context protocol, mcp server, mcp tool]
requires: [agentic-ai.tool-calling]
related: [agentic-ai.fundamentals.agent-loops, dotnet.api-design]
optional: []
prerequisites: [agentic-ai.tool-calling]
tags: [mcp, tool-calling, interop]
---

# MCP (Model Context Protocol)

## Purpose
Expose this project's tools/data to any MCP-compatible AI client through a
standard protocol, or consume another MCP server's tools from a .NET agent
— interoperability instead of a bespoke tool-calling integration per
client.

## When to Use
- Exposing internal capabilities (data access, actions) to external AI
  tools (Claude Code, Cursor, other MCP clients) in a standard way.
- Consuming an existing MCP server's tools from a .NET-based agent instead
  of writing a custom integration.
- Not required for an agent whose tools are entirely internal to one
  .NET application — plain `agentic-ai.tool-calling` is simpler when
  there's no cross-client interoperability need.

## Prerequisites
`agentic-ai.tool-calling` — an MCP server's tools follow the same design
principles.

## Inputs Required
Whether you're building an MCP server (exposing tools) or an MCP client
(consuming another server's tools), and the transport (stdio for local
processes, HTTP/SSE for remote).

## Engineering Principles
1. An MCP tool follows the same design discipline as any other agent tool
   (`agentic-ai.tool-calling`): precise schema, wraps an already-authorized
   operation, minimal/safe result payload.
2. An MCP server's authorization model must be explicit — who's calling it
   (a specific user's session, a service identity) and what that identity
   is allowed to do; MCP itself doesn't provide authorization, the server
   implementation must.
3. Treat an MCP client's tool-call requests as untrusted input at the
   server boundary, same as any external API request
   (`dotnet.security`) — the fact that the caller is "an AI assistant" via
   MCP doesn't change the trust boundary.
4. When consuming an external MCP server's tools, treat its tool
   descriptions and results as untrusted content flowing into your agent's
   context (`agentic-ai.ai-security`) — you don't control that server's
   implementation or its data.
5. Version the server's tool contract — MCP clients may cache tool
   definitions; a breaking change to a tool's schema needs the same care as
   any API breaking change (`dotnet.api-design`).

## Step-by-Step Workflow
### Building an MCP server
1. Identify which existing application operations should be exposed as MCP
   tools (same selection discipline as `agentic-ai.tool-calling`).
2. Implement the MCP server using the official/community .NET SDK,
   registering tool handlers that call into existing, already-authorized
   application services.
3. Define the authorization model explicitly — how the server identifies
   the calling context and enforces permissions per tool call.
4. Choose transport (stdio for local integration, HTTP/SSE for a remotely
   accessible server) based on the deployment/consumption model.

### Consuming an MCP server
1. Connect via the appropriate transport; treat the connection like any
   other external dependency (`dotnet.dotnet` — resilience, timeout).
2. Register the server's exposed tools into your agent's tool registry
   (`agentic-ai.tool-calling`), applying the same authorization scoping as
   any other tool.
3. Treat tool results from the external server as untrusted content in
   context (`agentic-ai.context-engineering`, `agentic-ai.ai-security`).

## Code Standards
MCP tool handlers are thin adapters over existing application services —
same as any other tool-calling handler (`agentic-ai.tool-calling`), not a
new business-logic surface that only exists for MCP.

## Architecture Constraints
An MCP server sits at the same boundary as any other externally-facing API
— it depends on Application, not directly on Domain/Infrastructure
internals (`dotnet.architecture.clean-architecture`).

## Security Considerations
- MCP server authorization must be explicit and enforced per tool call —
  don't assume "only trusted clients connect" as the security model.
- A stdio-transport MCP server inherits the permissions of the process that
  spawned it — be deliberate about what that process can access.
- Never expose a tool via MCP that performs an irreversible action without
  the same human-in-the-loop consideration as any other tool
  (`agentic-ai.human-in-the-loop`).

## Testing Requirements
Integration tests against the MCP server covering: a tool call succeeds for
an authorized context, is rejected for an unauthorized one, and a malformed
tool-call request is rejected safely (not with an unhandled exception
leaking internal detail).

## Common Mistakes
- Exposing an internal operation via MCP without adding the authorization
  check that operation would normally require through its usual entry
  point.
- Assuming an external MCP server's tool descriptions are trustworthy
  instructions rather than data to validate before acting on.
- No version/compatibility plan for a tool schema change, breaking clients
  that cached the old definition.

## Anti-Patterns
- **MCP as a shortcut around authZ**: building an MCP tool that skips
  authorization checks "because it's just for the AI assistant."
- **Blind trust in third-party MCP servers**: connecting to and executing
  tools from an MCP server without vetting what it actually does, treating
  it as equivalent to a first-party internal tool.

## Validation Checklist
- [ ] MCP server enforces explicit authorization per tool call.
- [ ] Tool handlers wrap existing, already-authorized application
      operations.
- [ ] External MCP server results are treated as untrusted content.
- [ ] Irreversible tools have a human-in-the-loop checkpoint.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; authorization
enforcement is covered by an integration test for both allow and deny
cases.

## Example
```csharp
// Minimal MCP server tool registration, wrapping an existing, authorized use case
mcpServer.RegisterTool(new McpToolDefinition
{
    Name = "get_order_status",
    Description = "Look up the status of an order the current user owns.",
    Handler = async (args, callContext, ct) =>
    {
        var userId = callContext.RequireAuthenticatedUserId(); // explicit authZ context
        var orderId = args.GetRequired<Guid>("orderId");
        var result = await orderQueryHandler.Handle(new GetOrderStatusQuery(orderId, userId), ct);
        return result.IsSuccess
            ? McpToolResult.Success(new { status = result.Value })
            : McpToolResult.SafeError("Order not found.");
    }
});
```

## Related Skills
- `agentic-ai.tool-calling` — the design discipline MCP tools follow.
- `dotnet.api-design` — contract/versioning principles applied to MCP tool
  schemas.
