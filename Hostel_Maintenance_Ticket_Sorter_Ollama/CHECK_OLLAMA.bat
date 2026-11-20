@echo off
setlocal
echo Checking Ollama local API...
curl.exe -sS --max-time 5 http://127.0.0.1:11434/api/tags
echo.
echo.
echo Installed model list:
where ollama >nul 2>nul
if not errorlevel 1 ollama list
if errorlevel 1 "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" list
pause
