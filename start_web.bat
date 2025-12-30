@echo off
echo ========================================
echo   RPA Bot - Web Interface Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version

echo.
echo [2/3] Installing/Updating dependencies...
pip install -r requirements_web.txt

echo.
echo [3/3] Starting Flask server...
echo.
echo ========================================
echo   Web interface will open at:
echo   http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app
python app.py

pause


