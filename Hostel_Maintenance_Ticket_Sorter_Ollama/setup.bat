@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Hostel Ticket Sorter - Setup
echo ============================================================
echo   HOSTEL MAINTENANCE TICKET SORTER - FIRST TIME SETUP
echo ============================================================
echo.
echo This setup installs Python packages, checks Ollama, and downloads
echo Qwen2.5 3B (about 1.9 GB). Internet is needed for first setup.
echo Later runs use the model locally - no paid API key.
echo.

set "OLLAMA_EXE="
where ollama >nul 2>nul
if not errorlevel 1 set "OLLAMA_EXE=ollama"
if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

if not defined OLLAMA_EXE (
  echo Ollama is not installed. Downloading official Windows installer...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe' } catch { Write-Host $_; exit 1 }"
  if errorlevel 1 goto :fail
  echo.
  echo Starting Ollama installer. Complete the installation, then run
  echo setup.bat again.
  start /wait "" "%TEMP%\OllamaSetup.exe"
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
  ) else (
    echo.
    echo Ollama was not detected after installation.
    echo Please finish the installer, reopen Command Prompt, and run setup.bat again.
    goto :fail
  )
)

echo [1/4] Checking Python...
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 (
    echo Could not create Python environment. Install Python 3.10 or newer.
    goto :fail
  )
)

echo [2/4] Installing required Python packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [3/4] Starting/checking local Ollama service...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  start "Ollama Local Server" "%OLLAMA_EXE%" serve
)

set "READY="
for /L %%i in (1,1,60) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
  if not errorlevel 1 set "READY=1"
  if defined READY goto :server_ready
  timeout /t 2 /nobreak >nul
)
echo Ollama did not become ready. Check whether the Ollama app is running.
goto :fail

:server_ready
echo [4/4] Downloading Qwen2.5 3B model (about 1.9 GB)...
"%OLLAMA_EXE%" pull qwen2.5:3b
if errorlevel 1 goto :fail

if not exist ".env" copy ".env.example" ".env" >nul
echo.
echo ============================================================
echo SETUP COMPLETE!
echo Run STARTUP.bat or RUN.bat to process complaints.csv.
echo ============================================================
pause
exit /b 0

:fail
echo.
echo SETUP FAILED. Read the message above, fix the issue, and run setup.bat again.
pause
exit /b 1
