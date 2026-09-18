---
id: rule.git
title: Git Rules
category: rule
tech_tags: [git, github]
triggers: [git rules, commit message rule, branch naming rule, force push rule]
severity: recommended
tags: [git]
---

# Git Rules

## One commit, one logical change

**Rule:** A commit contains exactly one logical change — a bug fix does not
also bundle a formatting pass or an unrelated refactor.

**Why:** A mixed commit is harder to review, harder to revert
independently, and harder to bisect when tracking down a regression.

**Applies to:** Every commit.

**Exception:** None.

---

## Commit messages explain why, not just what

**Rule:** A commit message's body (beyond the summary line) explains the
reasoning behind the change when it isn't obvious from the diff — not a
restatement of which files changed.

**Why:** The diff already shows what changed; the message earns its place
by adding context the diff can't convey.

**Applies to:** Every non-trivial commit.

**Exception:** A genuinely self-explanatory change (a typo fix) needs no
body.

---

## Never force-push a shared branch without explicit coordination

**Rule:** `git push --force` on a branch others may have pulled from is
never done without confirming with the user first, and never on a
protected/shared branch (main/master) at all except with explicit
instruction.

**Why:** A force-push can silently discard others' work with no easy
recovery.

**Applies to:** Every force-push.

**Exception:** The user explicitly requests it for their own branch, having
confirmed no one else depends on its current history.

---

## Never skip hooks or bypass signing without explicit instruction

**Rule:** `--no-verify`, `--no-gpg-sign`, or disabling commit signing is
never used to work around a failing check — the underlying issue is fixed
instead, unless the user explicitly asks to bypass it.

**Why:** Hooks and signing exist as a deliberate control; bypassing them
silently defeats their purpose.

**Applies to:** Every commit/push operation.

**Exception:** The user explicitly asks to bypass, understanding the
trade-off.

---

## A PR is scoped to one reviewable concern

**Rule:** A pull request bundles related changes serving one purpose — an
unrelated change goes in a separate PR even if it was convenient to make
alongside.

**Why:** A PR mixing concerns is harder to review thoroughly and harder to
revert selectively if one part causes a problem.

**Applies to:** Every PR.

**Exception:** A coordinated multi-part change the user explicitly wants
bundled.

---

## No secret in a commit, ever

**Rule:** Before staging, review what's actually included — a broad `git
add` is checked with `git status`/diff before committing, and any file
that might contain a secret is inspected first.

**Why:** A secret committed to git history requires rotation, not just
removal from a later commit — this is much more expensive to fix than to
prevent.

**Applies to:** Every commit.

**Exception:** None.
