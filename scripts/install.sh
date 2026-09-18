#!/usr/bin/env bash
# Installs the .NET AI Engineering Toolkit into a consuming project.
#
# Usage:
#   ./install.sh [--copy] [--adapter <name>]... [--target <path>]
#
#   --copy              Copy the toolkit instead of adding it as a git
#                        submodule (default: submodule). Used automatically
#                        if the target isn't a git repository.
#   --adapter <name>    Generate an entry-point file for this adapter.
#                        Repeatable. One of: claude, cursor, windsurf,
#                        copilot. (chatgpt/gemini have no file-based entry
#                        point in their default modes — see
#                        adapters/chatgpt.md / adapters/gemini.md instead.)
#   --target <path>     Target project root (default: current directory).
#   -h, --help          Show this help.
#
# See README.md's "Using this in a project" section for the resulting
# layout.

set -euo pipefail

TOOLKIT_REMOTE="${TOOLKIT_REMOTE:-https://github.com/msaeedm51/dotnet-agentic-ai-toolkit.git}"
TARGET="."
MODE="submodule"
ADAPTERS=()

usage() {
    sed -n '2,20p' "$0"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --copy) MODE="copy"; shift ;;
        --adapter) ADAPTERS+=("$2"); shift 2 ;;
        --target) TARGET="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
    esac
done

AI_DIR="$TARGET/.ai"
TOOLKIT_DIR="$AI_DIR/toolkit"
mkdir -p "$AI_DIR"

if [[ "$MODE" == "submodule" ]] && ! git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
    echo "Target is not a git repository; falling back to --copy mode." >&2
    MODE="copy"
fi

if [[ "$MODE" == "submodule" ]]; then
    if [[ -d "$TOOLKIT_DIR" ]]; then
        echo "$TOOLKIT_DIR already exists; skipping submodule add. Run" \
             "'git -C \"$TARGET\" submodule update --remote .ai/toolkit' to update it." >&2
    else
        git -C "$TARGET" submodule add "$TOOLKIT_REMOTE" .ai/toolkit
    fi
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TOOLKIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
    mkdir -p "$TOOLKIT_DIR"
    # rsync excludes .git; fall back to cp + rm if rsync isn't available.
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='.git' "$TOOLKIT_ROOT/" "$TOOLKIT_DIR/"
    else
        cp -R "$TOOLKIT_ROOT/." "$TOOLKIT_DIR/"
        rm -rf "$TOOLKIT_DIR/.git"
    fi
    echo "Copied toolkit to $TOOLKIT_DIR (not a submodule — update manually by re-running this script)."
fi

mkdir -p "$AI_DIR/overrides"

if [[ ! -f "$AI_DIR/config.yaml" ]]; then
    cat > "$AI_DIR/config.yaml" <<'YAML'
# See .ai/toolkit/schemas/config.schema.json for the full shape and
# .ai/toolkit/examples/ for filled samples per project archetype.
project:
  name: my-project
  domains: [dotnet]   # add "agentic-ai" if this project builds AI agents

backend:
  framework: aspnetcore

rules:
  strict_architecture: true
  require_tests: true
  require_security_review: true
YAML
    echo "Created $AI_DIR/config.yaml — edit it to match your project."
else
    echo "$AI_DIR/config.yaml already exists; left unchanged."
fi

entry_content() {
    cat <<'BODY'
# Project AI Instructions

This project uses the .NET AI Engineering Toolkit at .ai/toolkit/.

Before any non-trivial task, read .ai/toolkit/AGENTS.md (operating
principles + entry sequence) and .ai/toolkit/RULES.md (precedence), then
.ai/config.yaml for this project's stack. Resolve relevant
skills/agents/rules/workflows via .ai/toolkit/index/*.yaml per AGENTS.md
§4 rather than loading the whole toolkit.

.ai/overrides/*.md take precedence over toolkit defaults per RULES.md.
BODY
}

write_entry() {
    local path="$1"
    mkdir -p "$(dirname "$TARGET/$path")"
    if [[ -f "$TARGET/$path" ]]; then
        echo "$TARGET/$path already exists; not overwriting. See adapters/ for the expected content." >&2
    else
        entry_content > "$TARGET/$path"
        echo "Created $TARGET/$path"
    fi
}

for adapter in "${ADAPTERS[@]:-}"; do
    case "$adapter" in
        claude)   write_entry "CLAUDE.md" ;;
        cursor)   write_entry ".cursorrules" ;;
        windsurf) write_entry ".windsurfrules" ;;
        copilot)  write_entry ".github/copilot-instructions.md" ;;
        "") ;;
        *)
            echo "Unknown adapter '$adapter' — see adapters/generic.md to wire it up manually." >&2
            ;;
    esac
done

echo "Done. Toolkit installed at $TOOLKIT_DIR."
