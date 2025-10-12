# Requires -Version 3.0
param(
  [string]$PythonPath = ""
)
$ErrorActionPreference = 'Stop'

function Resolve-Python {
  param([string]$UserSpecified)
  if ($UserSpecified -and (Test-Path $UserSpecified)) { return $UserSpecified }
  if ($env:VIRTUAL_ENV) {
    $venvPy = Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe'
    if (Test-Path $venvPy) { return $venvPy }
  }
  $pyCmd = (Get-Command python -ErrorAction SilentlyContinue)
  if ($pyCmd) { return $pyCmd.Source }
  $launcher = (Get-Command py -ErrorAction SilentlyContinue)
  if ($launcher) { return 'py -3' }
  throw "No Python executable found. Install Python or specify -PythonPath"
}

function Invoke-Reload {
  param([string]$RepoRoot, [string]$Python)
  Write-Host "[Watcher] Reloading knowledge..." -ForegroundColor Cyan
  $reloadScript = Join-Path $RepoRoot 'scripts/reload_knowledge.py'
  if ($Python -eq 'py -3') {
    & py -3 $reloadScript | Write-Host
  } else {
    & $Python $reloadScript | Write-Host
  }
}

# Resolve repo root and python
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Resolve-Python -UserSpecified $PythonPath
$KnowledgeDir = Join-Path $RepoRoot 'knowledge'

if (-not (Test-Path $KnowledgeDir)) {
  Write-Warning "Knowledge directory not found at '$KnowledgeDir'. Creating it."
  New-Item -ItemType Directory -Path $KnowledgeDir -Force | Out-Null
}

# Setup file system watcher
$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $KnowledgeDir
$fsw.IncludeSubdirectories = $true
$fsw.Filter = '*.*'
$fsw.EnableRaisingEvents = $true

$script:pending = $false
$script:lastChange = Get-Date '1970-01-01'
$debounceSeconds = 2

$handler = {
  $script:pending = $true
  $script:lastChange = Get-Date
}

$subs = @()
$subs += Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $handler
$subs += Register-ObjectEvent -InputObject $fsw -EventName Created -Action $handler
$subs += Register-ObjectEvent -InputObject $fsw -EventName Deleted -Action $handler
$subs += Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $handler

Write-Host "[Watcher] Monitoring '$KnowledgeDir' (and subfolders)." -ForegroundColor Green
Write-Host "[Watcher] Will auto-reload knowledge on changes. Press Ctrl+C to stop." -ForegroundColor Green

try {
  while ($true) {
    Start-Sleep -Seconds 1
    if ($script:pending -and ((Get-Date) - $script:lastChange).TotalSeconds -ge $debounceSeconds) {
      $script:pending = $false
      try {
        Invoke-Reload -RepoRoot $RepoRoot -Python $Python
      } catch {
        Write-Warning ("[Watcher] Reload failed: {0}" -f $_)
      }
    }
  }
} finally {
  foreach ($s in $subs) { Unregister-Event -SourceIdentifier $s.Name -ErrorAction SilentlyContinue }
  $fsw.EnableRaisingEvents = $false
  $fsw.Dispose()
}
