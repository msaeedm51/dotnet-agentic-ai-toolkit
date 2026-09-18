---
id: dotnet.docker
title: Docker for .NET
category: skill
domain: dotnet
technologies: [docker, dotnet]
triggers: [dockerize, dockerfile, multi-stage build, container image, docker compose]
requires: []
related: [dotnet.linux, dotnet.azure]
optional: []
prerequisites: []
tags: [docker, containers]
---

# Docker for .NET

## Purpose
Build small, secure, fast-starting container images for .NET services using
multi-stage builds, and run them correctly in local development via
compose.

## When to Use
Any project targeting container-based deployment (Container Apps, AKS,
generic Linux hosting).

## Prerequisites
None.

## Inputs Required
Target runtime (Linux containers by default for .NET) and whether the
image needs to run as part of a multi-service local dev setup (compose).

## Engineering Principles
1. Multi-stage build: SDK image for build/publish, runtime (or
   `chiseled`/Alpine) image for the final layer — never ship the SDK image
   to production, it's far larger and has a bigger attack surface.
2. Run as a non-root user in the final image.
3. Copy only what's needed into the final image layer — `.dockerignore`
   excludes `bin/`, `obj/`, `.git/`, local secrets.
4. Layer caching: copy `.csproj`/`.sln` and restore before copying the rest
   of the source, so dependency restore is cached across builds that only
   change source code.
5. Explicit health check (`HEALTHCHECK` instruction or platform-level probe)
   so orchestrators know when the container is actually ready.

## Step-by-Step Workflow
1. Write a multi-stage `Dockerfile`: `build` stage restores + publishes,
   final stage copies only the published output onto a minimal runtime
   base image.
2. Add a non-root `USER` in the final stage.
3. Order `COPY` instructions to maximize layer cache reuse (project files
   before source).
4. Add `.dockerignore` covering `bin/`, `obj/`, `.vs/`, `.git/`, local
   `.env`/secrets files.
5. For local multi-service development, write `docker-compose.yml` wiring
   the app plus its real dependencies (database, cache) as containers.
6. Verify the image actually runs and passes its health check locally
   before treating the Dockerfile as done.

## Code Standards
Pin base image tags to a specific .NET version (`mcr.microsoft.com/dotnet/aspnet:8.0`),
not `latest`, for reproducible builds.

## Architecture Constraints
The image contains only the application and its runtime — no build tools,
no source code beyond what's needed to run, no dev-only dependencies.

## Security Considerations
Non-root user in the final image. No secret baked into an image layer
(even a `docker history` on a layer that later deleted a secret file can
still expose it) — pass secrets at runtime via environment/mounted secret,
never `COPY`.

## Testing Requirements
Verify the built image boots and its health check passes as part of CI,
not just that the `Dockerfile` builds.

## Common Mistakes
- Copying the entire source tree before restoring, breaking layer caching
  on every source change.
- Running as root in the final image with no stated reason.
- Baking a secret (even temporarily, then "removing" it in a later
  instruction) into an image layer — it's still recoverable from the layer
  history.

## Anti-Patterns
- **SDK image in production**: shipping the full SDK image instead of a
  runtime-only final stage — larger, slower to pull, bigger attack surface.
- **`latest` tag everywhere**: unpinned base images causing non-reproducible
  builds when the upstream tag moves.

## Validation Checklist
- [ ] Multi-stage build; final image doesn't contain the SDK.
- [ ] Runs as non-root.
- [ ] `.dockerignore` excludes build artifacts and secrets.
- [ ] Base image tags are pinned, not `latest`.
- [ ] Health check verified to actually pass after boot.

## Definition of Done
Meets `rules/definition-of-done.md`; the image builds, boots, and passes
its health check in CI.

## Example
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/Api/Api.csproj", "src/Api/"]
RUN dotnet restore "src/Api/Api.csproj"
COPY . .
RUN dotnet publish "src/Api/Api.csproj" -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
RUN adduser --disabled-password --gecos "" appuser
COPY --from=build /app/publish .
USER appuser
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health/live || exit 1
ENTRYPOINT ["dotnet", "Api.dll"]
```

## Related Skills
- `dotnet.linux` — the runtime environment the container executes in.
- `dotnet.azure` — deploying this image to Container Apps/AKS.
