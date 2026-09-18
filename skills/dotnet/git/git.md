---
id: dotnet.git
title: Git Hygiene
category: skill
domain: dotnet
technologies: [git, github]
triggers: [commit message, branch naming, pull request, rebase, merge conflict, git hygiene]
requires: []
related: [dotnet.docker]
optional: []
prerequisites: []
tags: [git, workflow]
---

# Git Hygiene

## Purpose
Keep history readable and bisectable, and pull requests reviewable — small,
focused commits with messages explaining why, not a play-by-play of what.

## When to Use
Every commit and PR. See `rules/git.md` for the enforceable rule list this
skill explains the reasoning for.

## Prerequisites
None.

## Inputs Required
None beyond the change being committed.

## Engineering Principles
1. A commit is one logical change — not "fix bug + also refactor unrelated
   thing + also update formatting everywhere."
2. Commit messages explain why, not just what — the diff already shows
   what changed; the message earns its place by adding context the diff
   can't.
3. A PR is reviewable in one sitting — if it's not, it's probably bundling
   unrelated changes that should be separate PRs.
4. Never rewrite published/shared history (`force-push` to a shared branch,
   `rebase -i` on commits others have already pulled) without explicit
   coordination.
5. Branch names describe the work (`feature/order-cancellation`,
   `fix/deadlock-in-submit`), not a ticket number alone with no other
   context.

## Step-by-Step Workflow
1. Before committing, review the actual diff (`git status`/`git diff`) —
   confirm nothing unrelated snuck in from a broad `git add`.
2. Stage and commit one logical change at a time.
3. Write the commit message: a concise summary line, then (if needed) a
   body explaining why this change was made, not a restatement of the diff.
4. Before opening a PR, confirm the branch is up to date with its target
   and resolve any conflicts by merging/rebasing per the project's
   convention — never by discarding either side's changes without review.
5. Keep the PR scoped to one concern; split unrelated changes into separate
   PRs even if they were convenient to make together.

## Code Standards
See `rules/git.md` for specific enforceable rules (commit message format,
branch naming, when to squash).

## Architecture Constraints
Not applicable.

## Security Considerations
Never commit a secret, credential, or `.env` file — if one is committed,
rotating the credential is required, not just removing it from a later
commit (history still contains it) (`dotnet.security`).

## Testing Requirements
Not applicable directly, though a PR should not merge with a failing test
suite (`rules/git.md`/CI gate).

## Common Mistakes
- A commit message that just restates the diff ("update OrderService.cs")
  instead of explaining why the change was made.
- Bundling a drive-by refactor into a bug-fix commit, making the fix harder
  to review and revert independently if needed.
- Force-pushing over a branch others have already pulled from, silently
  discarding their local history's base.

## Anti-Patterns
- **Kitchen-sink commit**: one commit touching unrelated files/concerns
  because it was convenient, not because it's one logical change.
- **WIP history left in a PR**: dozens of "wip," "fix typo," "actually fix
  it" commits left unsquashed in a PR meant for review, obscuring the
  actual logical changes.

## Validation Checklist
- [ ] Each commit is one logical change.
- [ ] Commit messages explain why, not just what.
- [ ] No secret/credential in the diff.
- [ ] PR is scoped to one concern and reviewable in one sitting.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/git.md`.

## Example
```
fix: prevent double-submission on slow network retry

Order submission was retried by the client on timeout, but the server had
no idempotency check, so a slow response could result in two orders being
created for one user action. Add an idempotency key requirement to the
submit endpoint.
```
Not:
```
update OrderController.cs
```

## Related Skills
- `dotnet.docker` — CI/CD pipeline that builds/tests the container image
  and gates merge on tests passing.
