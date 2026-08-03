# Builds dist\ClientMeetMatic.exe via PyInstaller.
#
# Usage (from anywhere):
#   powershell -File scripts\build_exe.ps1
#
# Always builds from an isolated virtualenv (.venv-build) containing only this project's
# dependencies, created on first run. Building against a Python install that also has
# unrelated packages on it (a data-science stack, other projects' deps, etc.) is not just
# messier output — it can make PyInstaller's dependency scanner hang for many minutes
# walking irrelevant packages, or crash entirely on a buggy hook for something you don't
# even use (hit this in practice with a stray `sentry_sdk` install pulled in by an
# unrelated package). The isolated venv sidesteps all of that.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    $venvPython = ".venv-build\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating isolated build venv (.venv-build)..." -ForegroundColor Cyan
        python -m venv .venv-build
        & $venvPython -m pip install -q --upgrade pip
        & $venvPython -m pip install -q -r requirements.txt -r requirements-build.txt
    }

    & ".venv-build\Scripts\pyinstaller.exe" clientmeetmatic.spec --noconfirm
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }
    Write-Host "Build complete: dist\ClientMeetMatic.exe" -ForegroundColor Green
} finally {
    Pop-Location
}
