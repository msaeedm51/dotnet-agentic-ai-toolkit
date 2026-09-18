# Templates

Project bootstrap scaffolds — **structure and key configuration files**,
not full runnable starter applications. This is a deliberate scope
decision (see `CHANGELOG.md` Batch A): a knowledge repository that also
tries to be a project generator doubles its maintenance surface for
limited benefit. Each template gives you:

- A `README.md` describing the folder layout for that architecture, with
  pointers to the relevant `skills/dotnet/` files for each part of it.
- `.editorconfig`, `Directory.Build.props`, `global.json`, `.gitignore` —
  the actual config every project needs, ready to copy in as-is.

## Available templates

| Template | Use when |
|---|---|
| `dotnet-api/` | A single, focused API service with no separate architecture layering — see `skills/dotnet/architecture/modular-monolith.md`'s "when NOT to" guidance and `rules/architecture.md` on choosing the simplest fit. |
| `clean-architecture/` | A service with real business logic worth isolating from frameworks — see `dotnet.architecture.clean-architecture`. |
| `modular-monolith/` | Multiple bounded contexts in one deployable — see `dotnet.architecture.modular-monolith`. |
| `library/` | A reusable class library (NuGet package or internal shared library), not a runnable service. |

## How to use one

1. Copy the chosen template folder's contents into your new project root.
2. Read its `README.md` and create the folders/projects it describes.
3. Run `scripts/install.sh`/`install.ps1` to add this toolkit itself at
   `.ai/toolkit/` and generate your adapter entry file(s).
4. Fill in `.ai/config.yaml` — see `examples/` for a filled sample matching
   this template's archetype.

## Why the same config files appear in every template

`.editorconfig`, `Directory.Build.props`, `global.json`, and `.gitignore`
are close to identical across templates on purpose — each template folder
is meant to be copied out as a **standalone unit** into a new project, so
duplicating these four small files across templates is the correct
trade-off (a new project shouldn't have to reach back into this toolkit
for its own build configuration). This is different from the "no
duplication" rule in `CONTRIBUTING.md`, which is about not duplicating
*engineering knowledge* — these are boilerplate config values, not
knowledge.
