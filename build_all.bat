@echo off
echo USB-Monitor Cross-Platform Build
echo =================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo Starting cross-platform build...
echo This will create both Windows .exe and macOS .app files!
echo.

python build_cross_platform.py

echo.
echo Build completed! Press any key to exit.
pause >nul
