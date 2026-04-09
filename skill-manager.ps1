#!/usr/bin/env pwsh

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $CliArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Help {
    @'
Usage:
  skill-manager.ps1
  skill-manager.ps1 shell
  skill-manager.ps1 help
  skill-manager.ps1 <skill-forge arguments>

Behavior:
  - No arguments: open the interactive menu for the current project directory
  - shell: open the runtime container's expert terminal
  - help, -h, --help: show this help text locally without starting Docker
  - check whether the local skill-forge repo is behind its upstream branch
  - offer to update with git pull --ff-only, then restart if the update succeeds
  - rebuild the runtime image automatically before each run
  - any other arguments: pass them through to the containerized skill-forge CLI

Examples:
  & "$HOME\skill-forge\skill-manager.ps1"
  & "$HOME\skill-forge\skill-manager.ps1" shell
  & "$HOME\skill-forge\skill-manager.ps1" validate
  & "$HOME\skill-forge\skill-manager.ps1" list --target codex --project /workspace/project --json
'@ | Write-Host
}

function Confirm-YesNo {
    param([string] $Prompt)

    $response = Read-Host -Prompt $Prompt
    return $response -match '^(?i:y|yes)$'
}

function Convert-ToDockerHostPath {
    param([string] $PathValue)

    $resolved = (Resolve-Path -LiteralPath $PathValue).ProviderPath
    return $resolved -replace '\\', '/'
}

function Test-Command {
    param([string] $Name)

    return $null -ne (Get-Command -Name $Name -ErrorAction SilentlyContinue)
}

function Update-RepoIfNeeded {
    param(
        [string] $RepoDir,
        [string[]] $ForwardArgs
    )

    if (-not (Test-Command "git")) {
        return
    }

    try {
        & git -C $RepoDir rev-parse --is-inside-work-tree *> $null
        if ($LASTEXITCODE -ne 0) {
            return
        }

        $upstreamRef = (& git -C $RepoDir rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>$null).Trim()
        if (-not $upstreamRef) {
            return
        }

        $currentBranch = (& git -C $RepoDir branch --show-current 2>$null).Trim()
        if (-not $currentBranch) {
            return
        }

        & git -C $RepoDir fetch --quiet *> $null
        if ($LASTEXITCODE -ne 0) {
            return
        }

        $aheadBehind = (& git -C $RepoDir rev-list --left-right --count "refs/heads/$currentBranch...$upstreamRef" 2>$null).Trim()
        if (-not $aheadBehind) {
            return
        }

        $counts = $aheadBehind -split '\s+'
        if ($counts.Length -lt 2) {
            return
        }

        $behindCount = [int] $counts[1]
        if ($behindCount -le 0) {
            return
        }

        Write-Host "A newer skill-forge version is available from $upstreamRef."
        if (-not (Confirm-YesNo "Update now with 'git pull --ff-only'? [y/N]")) {
            return
        }

        Write-Host "Updating skill-forge repo..."
        & git -C $RepoDir pull --ff-only
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Update complete. Restarting skill-manager.ps1..."
            & $PSCommandPath @ForwardArgs
            exit $LASTEXITCODE
        }

        Write-Host "Update failed. Continuing with the current local version."
    }
    catch {
        return
    }
}

if ($CliArgs.Count -gt 0 -and $CliArgs[0] -in @("help", "-h", "--help")) {
    Show-Help
    exit 0
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$composeFile = Join-Path $scriptDir "compose.yaml"
$projectDir = (Get-Location).ProviderPath
$projectHostDir = Convert-ToDockerHostPath $projectDir

Update-RepoIfNeeded -RepoDir $scriptDir -ForwardArgs $CliArgs

$previousProjectHostDir = $env:SKILL_FORGE_PROJECT_HOST_DIR
$previousHostUid = $env:HOST_UID
$previousHostGid = $env:HOST_GID

try {
    $env:SKILL_FORGE_PROJECT_HOST_DIR = $projectHostDir
    $env:HOST_UID = "0"
    $env:HOST_GID = "0"

    & docker compose -f $composeFile run --build --rm forge @CliArgs
    exit $LASTEXITCODE
}
finally {
    if ($null -eq $previousProjectHostDir) {
        Remove-Item Env:SKILL_FORGE_PROJECT_HOST_DIR -ErrorAction SilentlyContinue
    }
    else {
        $env:SKILL_FORGE_PROJECT_HOST_DIR = $previousProjectHostDir
    }

    if ($null -eq $previousHostUid) {
        Remove-Item Env:HOST_UID -ErrorAction SilentlyContinue
    }
    else {
        $env:HOST_UID = $previousHostUid
    }

    if ($null -eq $previousHostGid) {
        Remove-Item Env:HOST_GID -ErrorAction SilentlyContinue
    }
    else {
        $env:HOST_GID = $previousHostGid
    }
}
