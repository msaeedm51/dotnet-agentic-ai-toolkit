# Clean Architecture Template

Folder layout for a service where business logic is worth isolating from
frameworks and infrastructure. See `skills/dotnet/architecture/clean-architecture.md`
before building this out — don't use this template for a project with no
real business invariants (see that skill's Anti-Patterns section).

## Structure

```
src/
├── Domain/                  # Entities, value objects, domain services.
│   │                          No project references. See dotnet.architecture.ddd
│   │                          for how to model this.
│
├── Application/              # Use cases (commands/queries or app services),
│   │                          port interfaces (repositories, external
│   │                          service abstractions). References Domain only.
│   │                          See dotnet.architecture.cqrs if command/query
│   │                          separation fits; dotnet.architecture.result-rop
│   │                          for the Result type used for expected failures.
│
├── Infrastructure/           # EF Core DbContext + repository implementations,
│   │                          external service clients, messaging.
│   │                          References Application. See dotnet.efcore,
│   │                          dotnet.architecture.repository-specification.
│
└── Api/                       # Minimal API/controllers, DTOs, composition
                                root (Program.cs). References Application +
                                Infrastructure. See dotnet.aspnetcore,
                                dotnet.api-design.

tests/
├── Domain.Tests/              # Unit tests, no infrastructure — dotnet.testing
├── Application.Tests/         # Unit tests against ports (mocked), or real
│                                 Testcontainers integration tests for
│                                 anything relying on real infrastructure
│                                 behavior
├── Api.Tests/                 # WebApplicationFactory-based API tests
└── Architecture.Tests/        # Dependency-direction enforcement — see
                                  dotnet.architecture.clean-architecture's
                                  Testing Requirements
```

## Project references (enforce this — don't skip)

- `Domain` → (none)
- `Application` → `Domain`
- `Infrastructure` → `Application`
- `Api` → `Application`, `Infrastructure`

Add an architecture test (`Architecture.Tests/`) asserting `Domain` never
references `Infrastructure` or any framework package — this is what turns
the rule above from a convention into something CI actually enforces.

## Next steps

1. Set up `.ai/config.yaml` — copy `examples/config.clean-architecture-api.yaml`
   and adjust.
2. Run `scripts/install.sh`/`install.ps1` to add this toolkit and generate
   your AI assistant's entry-point file.
3. Follow `workflows/new-feature.md` for the first feature.
