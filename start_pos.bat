@echo off
echo Starting POS-V2 Python Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import tkinter, sqlite3" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Initialize database if it doesn't exist
if not exist "db\pos_system.db" (
    echo Initializing database...
    python db\init_db.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
)

REM Start the Python application
echo Starting POS-V2 Application...
python main.py

pause
