# Modular Monolith Template

Folder layout for multiple bounded contexts in one deployable. See
`skills/dotnet/architecture/modular-monolith.md` and
`skills/dotnet/architecture/ddd.md` (for identifying module boundaries)
before building this out.

## Structure

```text
src/
├── Host/                       # Composition root: Program.cs wires every
│                                  module's DI registrations together and
│                                  exposes the single ASP.NET Core app.
│
├── Modules/
│   ├── Orders/
│   │   ├── Orders.Domain/       # internal — not referenced outside this module
│   │   ├── Orders.Application/  # internal — public contract lives in Orders.Contracts
│   │   ├── Orders.Infrastructure/
│   │   └── Orders.Contracts/    # PUBLIC — the only thing other modules may reference:
│   │                              interfaces/DTOs/integration events
│   │
│   ├── Inventory/
│   │   ├── Inventory.Domain/
│   │   ├── Inventory.Application/
│   │   ├── Inventory.Infrastructure/
│   │   └── Inventory.Contracts/
│   │
│   └── <NextModule>/            # same four-project shape per module
│
└── SharedKernel/                 # Cross-cutting only (logging, auth
                                    primitives) — keep this deliberately
                                    small; see dotnet.architecture.modular-monolith's
                                    Common Mistakes on this becoming a dumping ground

tests/
├── Modules/<ModuleName>.Tests/   # per-module unit + integration tests
└── Architecture.Tests/           # asserts no module references another
                                     module's internal namespace — see
                                     dotnet.architecture.modular-monolith's
                                     Testing Requirements
```

## Rules to enforce from day one

- Each module gets its own `DbContext`, even against one physical
  database — see the skill's Code Standards on why.
- Cross-module interaction only through `<Module>.Contracts` or domain/
  integration events (`dotnet.architecture.domain-events-outbox`) — never
  a direct query into another module's tables.
- `Architecture.Tests` fails the build the moment a module references
  another module's internal namespace — add this test before the second
  module exists, not after a violation has already happened.

## Next steps

1. Set up `.ai/config.yaml` — copy `examples/config.modular-monolith.yaml`
   and adjust.
2. Run `scripts/install.sh`/`install.ps1`.
3. Identify your first two modules' bounded contexts before writing code
   — see `dotnet.architecture.ddd`.
