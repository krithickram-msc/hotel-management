@echo off
setlocal
cd /d "%~dp0"
call "%~dp0setup.bat"
if errorlevel 1 exit /b 1
call "%~dp0RUN.bat"
exit /b %errorlevel%
