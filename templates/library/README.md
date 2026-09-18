# Library Template

Folder layout for a reusable class library (an internal shared library or
a published NuGet package) — not a runnable service.

## Structure

```
src/
└── Contoso.SharedKernel/
    ├── Contoso.SharedKernel.csproj    # GenerateDocumentationFile=true,
    │                                    NuGet metadata — see
    │                                    Directory.Build.props
    └── ...

tests/
└── Contoso.SharedKernel.Tests/         # dotnet.testing — a library's public
                                          API surface is exactly what needs
                                          the most thorough test coverage,
                                          since consumers depend on it
                                          without visibility into internals

README.md            # this library's own README — usage examples,
                        installation, versioning policy (distinct from
                        this template's README)
CHANGELOG.md          # required for a published package — consumers need
                        to know what changed between versions
```

## Rules specific to a library

- Public API surface changes are backward-compatibility decisions —
  `rules/general.md`'s "consider backward compatibility" applies more
  strictly here than in an application, since you don't control every
  caller.
- No unnecessary dependencies (`rules/general.md`) matters even more for a
  library — every dependency you take becomes a transitive dependency for
  every consumer.
- Semantic versioning: a breaking change to the public API is a major
  version bump, always — document this policy in the library's own
  `CHANGELOG.md`.

## Next steps

1. Set the package metadata in `Directory.Build.props` (Authors, license,
   repository URL).
2. Run `scripts/install.sh`/`install.ps1` to add this toolkit for AI-
   assisted development (`.ai/config.yaml` → `project.type: library`).
3. Write the public API surface and its tests together — see
   `dotnet.testing`.
