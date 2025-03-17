@echo off
REM install.bat - PowerShell installation script wrapper

echo MagicalFlyingAlpaca Installer
echo ===========================
echo.

REM Check for administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: This script requires administrator privileges.
    echo Please right-click on this batch file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

echo Running installation script...
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

echo.
if %ERRORLEVEL% neq 0 (
    echo Installation encountered an error.
) else (
    echo Installation completed successfully.
)

pause
