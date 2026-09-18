<#
.SYNOPSIS
    Installs the .NET AI Engineering Toolkit into a consuming project.

.DESCRIPTION
    Adds this toolkit at .ai/toolkit (as a git submodule by default, or a
    plain copy with -Copy), seeds .ai/config.yaml if one doesn't already
    exist, and optionally generates adapter entry-point file(s).
    See README.md's "Using this in a project" section for the resulting
    layout.

.PARAMETER Copy
    Copy the toolkit instead of adding it as a git submodule. Used
    automatically if the target isn't a git repository.

.PARAMETER Adapter
    One or more adapter entry-point files to generate. Values: claude,
    cursor, windsurf, copilot. (chatgpt/gemini have no file-based entry
    point in their default modes — see adapters/chatgpt.md /
    adapters/gemini.md instead.)

.PARAMETER Target
    Target project root. Defaults to the current directory.

.PARAMETER ToolkitRemote
    Git URL to add as the submodule. Defaults to this toolkit's published
    repository.

.EXAMPLE
    ./install.ps1 -Adapter claude,copilot
#>
[CmdletBinding()]
param(
    [switch]$Copy,
    [ValidateSet('claude', 'cursor', 'windsurf', 'copilot')]
    [string[]]$Adapter = @(),
    [string]$Target = ".",
    [string]$ToolkitRemote = "https://github.com/msaeedm51/dotnet-agentic-ai-toolkit.git"
)

$ErrorActionPreference = "Stop"

$aiDir = Join-Path $Target ".ai"
$toolkitDir = Join-Path $aiDir "toolkit"
New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

$isGitRepo = $true
try {
    git -C $Target rev-parse --git-dir *> $null
} catch {
    $isGitRepo = $false
}

$mode = if ($Copy -or -not $isGitRepo) { "copy" } else { "submodule" }
if (-not $isGitRepo -and -not $Copy) {
    Write-Warning "Target is not a git repository; falling back to copy mode."
}

if ($mode -eq "submodule") {
    if (Test-Path $toolkitDir) {
        Write-Host "$toolkitDir already exists; skipping submodule add. Run 'git -C `"$Target`" submodule update --remote .ai/toolkit' to update it."
    } else {
        git -C $Target submodule add $ToolkitRemote .ai/toolkit
    }
} else {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $toolkitRoot = Split-Path -Parent $scriptDir
    New-Item -ItemType Directory -Force -Path $toolkitDir | Out-Null
    Get-ChildItem -Path $toolkitRoot -Force |
        Where-Object { $_.Name -ne ".git" } |
        ForEach-Object {
            Copy-Item -Path $_.FullName -Destination $toolkitDir -Recurse -Force
        }
    Write-Host "Copied toolkit to $toolkitDir (not a submodule — update manually by re-running this script)."
}

New-Item -ItemType Directory -Force -Path (Join-Path $aiDir "overrides") | Out-Null

$configPath = Join-Path $aiDir "config.yaml"
if (-not (Test-Path $configPath)) {
    @"
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
"@ | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "Created $configPath — edit it to match your project."
} else {
    Write-Host "$configPath already exists; left unchanged."
}

function Get-EntryContent {
    @"
# Project AI Instructions

This project uses the .NET AI Engineering Toolkit at .ai/toolkit/.

Before any non-trivial task, read .ai/toolkit/AGENTS.md (operating
principles + entry sequence) and .ai/toolkit/RULES.md (precedence), then
.ai/config.yaml for this project's stack. Resolve relevant
skills/agents/rules/workflows via .ai/toolkit/index/*.yaml per AGENTS.md
section 4 rather than loading the whole toolkit.

.ai/overrides/*.md take precedence over toolkit defaults per RULES.md.
"@
}

function Write-Entry([string]$RelativePath) {
    $fullPath = Join-Path $Target $RelativePath
    $dir = Split-Path -Parent $fullPath
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (Test-Path $fullPath) {
        Write-Warning "$fullPath already exists; not overwriting. See adapters/ for the expected content."
    } else {
        Get-EntryContent | Out-File -FilePath $fullPath -Encoding utf8
        Write-Host "Created $fullPath"
    }
}

foreach ($a in $Adapter) {
    switch ($a) {
        "claude"   { Write-Entry "CLAUDE.md" }
        "cursor"   { Write-Entry ".cursorrules" }
        "windsurf" { Write-Entry ".windsurfrules" }
        "copilot"  { Write-Entry ".github/copilot-instructions.md" }
    }
}

Write-Host "Done. Toolkit installed at $toolkitDir."
