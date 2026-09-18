# .NET API Template (Vertical Slice, No Forced Layering)

Folder layout for a small, single-purpose API service with no invariants
complex enough to justify Clean Architecture's layering
(`rules/architecture.md` — prefer the simplest architecture that satisfies
requirements). If this service later grows real business logic worth
isolating, migrate to `templates/clean-architecture/` deliberately, not by
accretion.

## Structure

```
src/
└── Api/
    ├── Features/
    │   ├── Notifications/
    │   │   ├── SendNotification.cs      # endpoint + request/response DTOs +
    │   │   │                              handler logic co-located — see
    │   │   │                              dotnet.aspnetcore
    │   │   └── SendNotificationTests.cs  # or in tests/, per project convention
    │   └── <NextFeature>/
    │       └── ...
    ├── Infrastructure/                   # DbContext, external clients —
    │                                        still separated from Features/
    │                                        even without full layering
    └── Program.cs                         # composition root

tests/
└── Api.Tests/                             # WebApplicationFactory-based —
                                              see dotnet.testing
```

## When this stops fitting

If you find yourself repeatedly duplicating validation/authorization logic
across features, or a business rule needs to be enforced regardless of
which feature triggers it, that's the signal to introduce a shared
Application/Domain layer — see `dotnet.architecture.clean-architecture`,
and treat the migration as a deliberate architecture decision
(`workflows/architecture-decision.md`), not silent scope creep.

## Next steps

1. Set up `.ai/config.yaml` — copy `examples/config.minimal-api.yaml` and
   adjust.
2. Run `scripts/install.sh`/`install.ps1`.
3. Follow `workflows/api-development.md` for the first endpoint.
