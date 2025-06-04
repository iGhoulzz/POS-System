@echo off
echo Testing Electron Kiosk Application...
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Starting Electron application...
npx electron . --dev
pause
