# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.x (latest `master`) | Yes |
| 0.x (pre-release) | No |

## Reporting a vulnerability

Do not open a public issue for a security report. Use GitHub's private
reporting instead: this repo's **Security** tab → **Report a vulnerability**
(GitHub Security Advisories). This applies to:

- `retrieval/` — the Python index store, MCP server, and embedding
  providers (e.g. injection, unsafe deserialization, credential handling).
- `scripts/install.sh` / `install.ps1` — the install/bootstrap scripts.
- `schemas/` / `scripts/validate.py` — anything that could let malformed
  content bypass validation in a way that's exploitable, not just
  incorrect.

A skill or rule file recommending an outdated or suboptimal practice is a
normal content issue, not a security report — file that per
`CONTRIBUTING.md`'s "Reporting a problem" section instead.

## Response

This is a community-maintained toolkit with no formal SLA. Reports are
acknowledged and triaged as soon as practical; a fix ships as an ordinary
PR once confirmed, with the report kept private until then.
