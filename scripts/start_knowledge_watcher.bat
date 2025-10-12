@echo off
setlocal
set REPO=%~dp0..
set SCRIPT=%REPO%\scripts\watch_knowledge.ps1

REM Launch minimized and bypass execution policy for convenience
powershell -NoProfile -WindowStyle Minimized -ExecutionPolicy Bypass -File "%SCRIPT%"

endlocal
