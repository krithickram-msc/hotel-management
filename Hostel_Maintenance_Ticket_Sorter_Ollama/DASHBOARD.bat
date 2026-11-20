@echo off
setlocal
cd /d "%~dp0"
title HostelOps - Advanced Dashboard
echo.
echo  HOSTELOPS - ADVANCED MAINTENANCE COMMAND CENTER
echo  Starting local dashboard (no AI model download required)...
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 dashboard.py
  goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python dashboard.py
  goto end
)
echo Python was not found. Install Python 3.11 or newer, then retry.
pause
:end
pause
