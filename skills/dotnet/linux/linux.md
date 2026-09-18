---
id: dotnet.linux
title: Linux Hosting for .NET
category: skill
domain: dotnet
technologies: [linux, nginx, systemd, dotnet]
triggers: [linux hosting, nginx reverse proxy, systemd service, https configuration, linux deployment]
requires: []
related: [dotnet.docker, dotnet.azure]
optional: []
prerequisites: []
tags: [linux, hosting]
---

# Linux Hosting for .NET

## Purpose
Host a .NET application directly on Linux (non-containerized or
container-adjacent) correctly: reverse proxy, TLS termination, process
management, and log/observability wiring.

## When to Use
Self-managed Linux hosting (VM, bare metal) rather than a managed platform
(Azure App Service/Container Apps). Often paired with `dotnet.docker` if
the process itself runs containerized on that Linux host.

## Prerequisites
None.

## Inputs Required
Whether TLS terminates at the reverse proxy or the app itself, and the
process manager in use (systemd is the default assumption here).

## Engineering Principles
1. Kestrel sits behind a reverse proxy (Nginx) in production — Kestrel
   itself is a capable server but the proxy handles TLS termination,
   request buffering, and static content more robustly at the edge.
2. TLS terminates at the proxy (or via a sidecar), with the proxy
   forwarding to Kestrel over HTTP on localhost/private network — configure
   `ForwardedHeaders` middleware so the app sees the real client IP/scheme.
3. The app runs as a systemd service (not a manually-started process) so it
   restarts on crash and starts on boot, with resource limits set
   deliberately.
4. Logs go to stdout/stderr (captured by systemd/journald) or a structured
   sink, not an ad hoc file the app manages itself.
5. Run the app as a dedicated non-root service user, not root.

## Step-by-Step Workflow
1. Publish the app (`dotnet publish`) for the target runtime identifier.
2. Create a systemd unit file: working directory, `ExecStart`, restart
   policy, resource limits, and the dedicated service user.
3. Configure Nginx as a reverse proxy: TLS termination (via a real
   certificate, e.g. Let's Encrypt), proxying to Kestrel's local port,
   forwarding relevant headers (`X-Forwarded-For`, `X-Forwarded-Proto`).
4. Add `app.UseForwardedHeaders()` in the ASP.NET Core pipeline configured
   to trust the proxy's forwarded headers.
5. Verify the health check endpoint is reachable through the proxy and
   wire it to whatever monitors the service.

## Code Standards
`ForwardedHeadersOptions` explicitly lists trusted proxies/networks —
never blindly trust all forwarded headers from any source.

## Architecture Constraints
The app doesn't handle TLS certificate management itself when a reverse
proxy is in front of it — that's the proxy's/certbot's responsibility.

## Security Considerations
Service user has no more filesystem/network access than the app needs.
Nginx configuration disables weak TLS versions/ciphers. Firewall rules
restrict direct access to Kestrel's port from outside the host (only the
proxy should reach it).

## Testing Requirements
Verify the health check is reachable end-to-end (through the proxy, over
TLS) after any hosting configuration change, not just directly against
Kestrel.

## Common Mistakes
- Exposing Kestrel directly to the internet without a reverse proxy in
  front of it.
- Running the app as root "to avoid permission issues" instead of granting
  the service user the specific access it needs.
- Forgetting `UseForwardedHeaders()`, so the app sees the proxy's IP/scheme
  instead of the real client's — breaks IP-based logic and HTTPS-only
  redirects.

## Anti-Patterns
- **Manually started process**: running the app with `dotnet Api.dll &` in
  a terminal instead of a supervised systemd service — no auto-restart, no
  boot-time start, no resource limits.
- **Trust-all forwarded headers**: accepting `X-Forwarded-*` headers from
  any source instead of restricting to the known proxy's address.

## Validation Checklist
- [ ] App runs under systemd with restart-on-failure.
- [ ] TLS terminates at the reverse proxy with a valid certificate.
- [ ] `ForwardedHeadersOptions` restricted to trusted proxy addresses.
- [ ] Service runs as a non-root, least-privilege user.
- [ ] Health check reachable end-to-end through the proxy.

## Definition of Done
Meets `rules/definition-of-done.md`; health check verified reachable
through the full proxy/TLS path.

## Example
```ini
# /etc/systemd/system/myapi.service
[Unit]
Description=My API
After=network.target

[Service]
WorkingDirectory=/var/www/myapi
ExecStart=/usr/bin/dotnet /var/www/myapi/Api.dll
Restart=always
RestartSec=5
User=myapi-svc
Environment=ASPNETCORE_URLS=http://localhost:5000
Environment=ASPNETCORE_ENVIRONMENT=Production

[Install]
WantedBy=multi-user.target
```
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass         http://localhost:5000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

## Related Skills
- `dotnet.docker` — containerized alternative to bare-metal Linux hosting.
- `dotnet.azure` — managed-platform alternative to self-managed Linux.
