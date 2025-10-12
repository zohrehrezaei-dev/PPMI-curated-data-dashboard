@echo off
echo Stopping PPMI Dashboard...
taskkill /F /IM python.exe /T >nul 2>&1
echo Dashboard stopped.
pause