@echo off
echo 🚀 Starting POS V2 Kiosk Application...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js is installed
echo.

REM Change to the directory containing this script
cd /d "%~dp0"

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ ERROR: package.json not found
    echo Make sure you're running this from the kiosk_electron directory
    pause
    exit /b 1
)

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
    echo.
)

REM Create app-data directory if it doesn't exist
if not exist "app-data" (
    echo 📁 Creating app-data directory...
    mkdir app-data
    echo ✅ App-data directory created
)

REM Clear any existing cache issues
if exist "app-data\Cache" (
    echo 🧹 Clearing cache...
    rmdir /s /q "app-data\Cache" 2>nul
    echo ✅ Cache cleared
)

if exist "app-data\GPUCache" (
    echo 🧹 Clearing GPU cache...
    rmdir /s /q "app-data\GPUCache" 2>nul
    echo ✅ GPU cache cleared
)

if exist "app-data\Local Storage" (
    echo 🧹 Clearing local storage...
    rmdir /s /q "app-data\Local Storage" 2>nul
    echo ✅ Local storage cleared
)

REM Set environment variables to fix cache issues
set ELECTRON_ENABLE_LOGGING=1
set ELECTRON_DISABLE_SECURITY_WARNINGS=1
set ELECTRON_NO_ATTACH_CONSOLE=1

echo.
echo 🎯 Launching kiosk interface...
echo.

REM Start the application
call npm start

echo.
echo 📋 Application has been closed.
pause
