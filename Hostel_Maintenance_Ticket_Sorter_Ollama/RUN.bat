@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Hostel Maintenance Ticket Sorter
if not exist ".venv\Scripts\python.exe" (
  echo Please run setup.bat first.
  pause
  exit /b 1
)
if not exist ".env" copy ".env.example" ".env" >nul

set "OLLAMA_EXE="
where ollama >nul 2>nul
if not errorlevel 1 set "OLLAMA_EXE=ollama"
if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not defined OLLAMA_EXE (
  echo Ollama is missing. Run setup.bat.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 start "Ollama Local Server" "%OLLAMA_EXE%" serve

echo Waiting for Ollama...
set "READY="
for /L %%i in (1,1,30) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
  if not errorlevel 1 set "READY=1"
  if defined READY goto :ready
  timeout /t 2 /nobreak >nul
)
echo Ollama is not responding. Open the Ollama app and try again.
pause
exit /b 1

:ready
echo Running ticket sorter with local Qwen2.5 3B...
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
  echo The sorter reported an error. Check the message above.
  pause
  exit /b 1
)
echo.
echo Finished. Review work_orders.csv, results.csv, needs_info.csv and summary.txt.
echo Warden review is required. The program does not close tickets.
pause
