<#
.SYNOPSIS
  One-command NutriMe install for Windows 10/11 (issue #34).

.DESCRIPTION
  Run from the NutriMe folder in PowerShell:
      powershell -ExecutionPolicy Bypass -File scripts\install-windows.ps1

  Installs what's missing (Ollama, uv), sets up NutriMe, downloads the
  local model, copies the bundled recipe collection, vets it, takes a
  first backup and registers NutriMe to start when you sign in.
  Safe to run again: every step skips work that's already done.

.PARAMETER Model
  Local model to download (default qwen3:8b).
.PARAMETER NoAutostart
  Don't register the sign-in task.
.PARAMETER Uninstall
  Remove the scheduled tasks only. Your data in %USERPROFILE%\.nutrime stays.
#>
param(
    [string]$Model = "qwen3:8b",
    [switch]$NoAutostart,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
$TaskName = "NutriMe"
$DataDir = if ($env:NUTRIME_DATA_DIR) { $env:NUTRIME_DATA_DIR } else { Join-Path $env:USERPROFILE ".nutrime" }

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Green }
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "$TaskName crawl" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed the '$TaskName' tasks. Your data in $DataDir is untouched."
    exit 0
}

if (-not (Test-Path (Join-Path $Repo "pyproject.toml"))) {
    throw "Run this from inside the NutriMe folder (couldn't find pyproject.toml in $Repo)."
}

Step "Checking for Ollama (runs the local model)"
if (-not (Have "ollama")) {
    if (-not (Have "winget")) { throw "winget isn't available. Install Ollama by hand from https://ollama.com, then run this again." }
    winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    Refresh-Path
}

Step "Checking for uv (installs Python and NutriMe's dependencies)"
if (-not (Have "uv")) {
    if (Have "winget") {
        winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements
    } else {
        powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    }
    Refresh-Path
}

Push-Location $Repo
try {
    Step "Installing NutriMe"
    uv sync --no-dev

    Step "Creating your data folder at $DataDir"
    uv run --no-dev nutrime init --data-dir "$DataDir" | Out-Null

    $recipes = Join-Path $DataDir "corpus\recipes"
    if (-not (Get-ChildItem $recipes -Filter *.md -ErrorAction SilentlyContinue | Select-Object -First 1)) {
        Step "Copying the bundled recipe collection"
        Copy-Item -Recurse -Force (Join-Path $Repo "corpus\recipes\*") $recipes
    }

    Step "Checking recipes (vetting)"
    uv run --no-dev nutrime recipes vet --data-dir "$DataDir"

    Step "Downloading the local model $Model (several GB, one time)"
    try { ollama pull $Model } catch { Write-Warning "Model download didn't finish. Run 'ollama pull $Model' later; everything except plan-making works without it." }

    Step "Taking a first backup"
    uv run --no-dev nutrime backup --data-dir "$DataDir"

    if (-not $NoAutostart) {
        Step "Starting NutriMe when you sign in"
        $uv = (Get-Command uv).Source
        $action = New-ScheduledTaskAction -Execute $uv `
            -Argument "run --no-dev --directory `"$Repo`" nutrime serve --data-dir `"$DataDir`"" `
            -WorkingDirectory $Repo
        $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
            -Settings $settings -Description "NutriMe home server (localhost:8765)" -Force | Out-Null
        Start-ScheduledTask -TaskName $TaskName

        Step "Collecting new recipes weekly (Sunday 3 am; sites' robots.txt decides)"
        $crawlAction = New-ScheduledTaskAction -Execute $uv `
            -Argument "run --no-dev --directory `"$Repo`" nutrime recipes crawl --data-dir `"$DataDir`"" `
            -WorkingDirectory $Repo
        $crawlTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
        $crawlSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries
        Register-ScheduledTask -TaskName "$TaskName crawl" -Action $crawlAction -Trigger $crawlTrigger `
            -Settings $crawlSettings -Description "NutriMe weekly recipe collection" -Force | Out-Null
    }

    Step "Checking everything"
    uv run --no-dev nutrime doctor --data-dir "$DataDir"
} finally {
    Pop-Location
}

Write-Host "`nDone. Open http://localhost:8765 in your browser." -ForegroundColor Green
Write-Host "Tip: a laptop that sleeps stops serving. Settings > System > Power to keep it awake while plugged in."
