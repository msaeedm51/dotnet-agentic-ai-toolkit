---
id: agentic-ai.human-in-the-loop
title: Human-in-the-Loop
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [human in the loop, approval workflow, irreversible action confirmation, agent needs approval]
requires: []
related: [agentic-ai.guardrails, agentic-ai.tool-calling, dotnet.architecture.background-processing]
optional: []
prerequisites: []
tags: [agents, human-in-the-loop, safety]
---

# Human-in-the-Loop

## Purpose
Require explicit human approval before an agent takes an action that's
irreversible, costly, or high-risk — the concrete mechanism, not just a
prompt instruction, that stops an agent from acting on a bad decision.

## When to Use
Any tool call that: sends something externally (email, message, webhook),
moves money, deletes or overwrites data with no easy recovery, publishes
content, or otherwise can't be cleanly undone. Not needed for read-only or
easily-reversible actions — gating everything erodes the agent's
usefulness and trains users to rubber-stamp approvals without reading them.

## Prerequisites
None.

## Inputs Required
Which specific actions in this system are irreversible/high-risk (a
concrete list, not a vague sense of "risky stuff") and who the appropriate
approver is for each.

## Engineering Principles
1. The checkpoint is enforced in code (the tool literally cannot execute
   without an approval record), not just requested via prompt instructions
   the model might skip under the right adversarial input
   (`agentic-ai.ai-security`).
2. The approval request shows the approver exactly what will happen —
   concrete parameters, not a vague summary — so approval is informed, not
   reflexive.
3. A pending approval has a timeout/expiry — an agent run waiting forever
   on an approval that never comes needs a defined resolution (fail, escalate,
   or expire the request).
4. Approval fatigue is a real risk — gate only genuinely high-risk actions;
   over-gating low-risk ones trains approvers to click through without
   reading, defeating the control.
5. Log every approval decision (who, when, what was approved, what was
   actually executed) for audit — this is often a compliance requirement,
   not just good practice.

## Step-by-Step Workflow
1. Identify the specific tool calls that need a human checkpoint (from the
   concrete list of irreversible/high-risk actions).
2. Implement the checkpoint so the tool call is blocked (not executed)
   until an approval record exists — e.g. the agent loop pauses, persists
   the pending action, and the actual execution happens only after an
   approval event.
3. Present the pending action to the approver with concrete, specific
   detail (not a paraphrase) — what will be sent, to whom, for how much.
4. Set a timeout for the approval; define what happens if it expires
   (cancel the action, escalate, or re-prompt).
5. Log the full decision trail: who approved/denied, when, and confirm what
   was actually executed matches what was approved.

## Code Standards
The approval gate is a first-class step in the agent's control flow (e.g. a
distinct `PendingApproval` state), not a prompt instruction hoping the
model asks first.

## Architecture Constraints
Approval state is persisted (not just held in memory in a long-running
process) so an approval can be granted asynchronously — a user approving
an hour later must still result in correct execution, not a lost/expired
in-memory state that silently never resumes.

## Security Considerations
The approval mechanism itself must be tamper-resistant — an approval
record must be traceable to an authenticated approver, and the exact
parameters approved must match what's executed (no substituting a
different action after approval, e.g. via a race condition or a mutable
pending-action record).

## Testing Requirements
Test that a gated tool call cannot execute without an approval record, that
an expired approval doesn't execute, and that what's executed exactly
matches what was approved (no drift between the two).

## Common Mistakes
- Gating the action only in the prompt ("ask the user before sending")
  instead of in code — an adversarial input or a model mistake can skip the
  prompt-level ask.
- No timeout, so an agent run hangs indefinitely on an approval that never
  arrives.
- Gating too many low-risk actions, causing approval fatigue and rubber-
  stamping.

## Anti-Patterns
- **Prompt-only gating**: relying entirely on "please confirm with the user
  before doing X" in the system prompt as the actual control.
- **Approve-then-substitute**: approving one specific action but executing
  a different one due to a race condition or mutable state between
  approval and execution.

## Validation Checklist
- [ ] Irreversible/high-risk actions are identified explicitly, not
      guessed at.
- [ ] The checkpoint is enforced in code, blocking execution without an
      approval record.
- [ ] The approval request shows concrete, specific action detail.
- [ ] A timeout/expiry is defined for pending approvals.
- [ ] The full decision trail is logged.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; a test
proves the gated action cannot execute without a valid, matching approval
record.

## Example
```csharp
public sealed class SendEmailTool(IApprovalStore approvals, IEmailSender sender) : IAgentTool<SendEmailArgs>
{
    public async Task<ToolResult> ExecuteAsync(SendEmailArgs args, AgentContext ctx, CancellationToken ct)
    {
        var request = PendingApproval.For(args, ctx.RunId);
        await approvals.RequestAsync(request, ct); // blocks here; agent run pauses

        var decision = await approvals.WaitForDecisionAsync(request.Id, timeout: TimeSpan.FromHours(1), ct);
        if (decision is not { Approved: true } || decision.ApprovedParametersHash != request.ParametersHash)
            return ToolResult.SafeError("Action was not approved.");

        await sender.SendAsync(args.To, args.Subject, args.Body, ct);
        return ToolResult.Success(new { sent = true });
    }
}
```

## Related Skills
- `agentic-ai.guardrails` — other automated (non-human) safety checks.
- `agentic-ai.tool-calling` — where this checkpoint is inserted.
- `dotnet.architecture.background-processing` — hosting a long-running,
  pausable agent run awaiting approval.
