@echo off
REM Simple script to run the setup script with Python on Windows

REM Check for Python 3
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the setup script
python setup.py %*

REM Pause to see any output before closing
pause