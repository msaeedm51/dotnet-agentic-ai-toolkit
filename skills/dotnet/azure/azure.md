---
id: dotnet.azure
title: Azure Deployment Patterns
category: skill
domain: dotnet
technologies: [azure, dotnet]
triggers: [azure deployment, app service, azure container apps, key vault, managed identity, azure sql]
requires: []
related: [dotnet.docker, dotnet.dotnet]
optional: []
prerequisites: []
tags: [azure, deployment]
---

# Azure Deployment Patterns

## Purpose
Deploy .NET services to Azure using managed identity for credential-free
service-to-service auth, Key Vault for secrets, and the App
Service/Container Apps/AKS tier appropriate to the project's actual scale
needs.

## When to Use
The project's `.ai/config.yaml` → `deployment.platform: azure`.

## Prerequisites
`dotnet.dotnet` for configuration/hosting fundamentals; `dotnet.docker` if
targeting Container Apps/AKS.

## Inputs Required
Expected scale/traffic pattern (drives the choice between App Service,
Container Apps, and AKS) and what Azure services the app depends on
(database, storage, Key Vault, Service Bus).

## Engineering Principles
1. Use managed identity for Azure-to-Azure authentication (app → Key Vault,
   app → Azure SQL/PostgreSQL, app → Storage) instead of connection strings
   with embedded credentials wherever the target supports it.
2. Secrets (third-party API keys, anything not Azure-AD-authenticatable)
   live in Key Vault, referenced via configuration, never in
   `appsettings.json` or app settings in plaintext for anything sensitive.
3. Choose the compute tier for the actual requirement: App Service for a
   straightforward web app with no container-specific need, Container Apps
   for containerized microservices with autoscaling and Dapr integration
   needs, AKS only when the project genuinely needs Kubernetes-level
   control — don't default to the most complex option.
4. Health checks (`dotnet.dotnet`) wired to the platform's health probe
   mechanism so unhealthy instances are taken out of rotation automatically.
5. Configuration via Azure App Configuration or environment-specific app
   settings, following the Options pattern in code either way.

## Step-by-Step Workflow
1. Confirm the compute tier already chosen for the project (or propose one
   based on the actual scale/container requirement, escalating to
   `agent.architect` if undecided).
2. Configure managed identity for the app's Azure resource dependencies.
3. Move any non-Azure-AD-authenticatable secret to Key Vault, referenced
   from configuration.
4. Wire health check endpoints to the platform's probe configuration
   (App Service health check path, Container Apps liveness/readiness
   probes).
5. Set up CI/CD (`dotnet.docker`/GitHub Actions) to build, test, and deploy
   to the target environment, with the deployment gated on tests passing.

## Code Standards
Configuration binds to typed options (`dotnet.dotnet`); no direct
`Environment.GetEnvironmentVariable` calls scattered through business
logic.

## Architecture Constraints
Deployment platform choice is an architecture decision
(`agent.architect`) when not already made — don't pick a tier unilaterally
mid-feature-implementation.

## Security Considerations
No connection string or API key in source control, app settings blade
screenshots in documentation, or logs. Managed identity scoped to the
minimum role assignment needed (e.g. `Key Vault Secrets User`, not
`Owner`).

## Testing Requirements
Verify configuration binding and health check wiring with an integration
test that boots the host with production-like configuration shape (values
can be fakes, but the shape/keys must match).

## Common Mistakes
- Using a connection string with an embedded password for Azure SQL instead
  of managed identity + Azure AD authentication.
- Choosing AKS by default for a simple service with no real need for
  Kubernetes-level control, taking on operational complexity with no
  corresponding benefit.
- Forgetting to wire health checks to the platform probe, so an unhealthy
  instance keeps receiving traffic.

## Anti-Patterns
- **Secrets in app settings**: storing a third-party API key directly in
  App Service configuration instead of Key Vault, especially when it's
  visible to anyone with portal read access.
- **Over-provisioned compute**: AKS for a single low-traffic service that
  App Service or Container Apps would serve with far less operational
  overhead.

## Validation Checklist
- [ ] Managed identity used for Azure-to-Azure auth where supported.
- [ ] Non-Azure-AD secrets are in Key Vault, not app settings/source.
- [ ] Health checks wired to the platform's probe mechanism.
- [ ] Compute tier matches the actual scale/container requirement.

## Definition of Done
Meets `rules/definition-of-done.md`; deployment configuration verified
against a non-production environment before targeting production.

## Example
```csharp
builder.Configuration.AddAzureAppConfiguration(options =>
    options.Connect(new Uri(builder.Configuration["AppConfig:Endpoint"]!), new DefaultAzureCredential())
        .ConfigureKeyVault(kv => kv.SetCredential(new DefaultAzureCredential())));

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default"),
        sql => sql.EnableRetryOnFailure()));
// Connection string references Azure SQL with Authentication=Active Directory Managed Identity
```

## Related Skills
- `dotnet.docker` — containerization for Container Apps/AKS targets.
- `dotnet.dotnet` — configuration/health-check foundations this builds on.
