param(
  [string]$TaskName = "AgentZeroKnowledgeWatcher"
)
$ErrorActionPreference = 'Stop'

try {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
  Write-Host "Scheduled task '$TaskName' removed." -ForegroundColor Yellow
} catch {
  Write-Warning "Failed to remove scheduled task '$TaskName': $_"
}
