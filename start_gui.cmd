@echo off
echo ===============================================
echo HAR-ANALYZE Web GUI Launcher
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    echo.
    pause
    exit /b 1
)

echo Python detected: 
python --version

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies may not have installed correctly
    echo The GUI may still work with basic functionality
    echo.
)

echo.
echo ===============================================
echo Starting HAR-ANALYZE Web GUI...
echo ===============================================
echo.
echo The web interface will open at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

python app.py

echo.
echo ===============================================
echo HAR-ANALYZE Web GUI has stopped
echo ===============================================
pause
