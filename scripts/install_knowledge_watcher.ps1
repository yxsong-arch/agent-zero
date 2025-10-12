param(
  [string]$TaskName = "AgentZeroKnowledgeWatcher",
  [string]$PythonPath = ""
)
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$script = Join-Path $repoRoot 'scripts/watch_knowledge.ps1'
if (-not (Test-Path $script)) { throw "watch_knowledge.ps1 not found at $script" }

# Build action command
$ps = (Get-Command powershell).Source
$argList = "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
if ($PythonPath) { $argList += " -PythonPath `"$PythonPath`"" }
$action = New-ScheduledTaskAction -Execute $ps -Argument $argList -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register task for current user
try {
  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Auto-reload Agent Zero knowledge on file changes" -ErrorAction Stop
  Write-Host "Scheduled task '$TaskName' created. It will start the watcher at logon." -ForegroundColor Green
} catch {
  Write-Error "Failed to create scheduled task: $_"
}
