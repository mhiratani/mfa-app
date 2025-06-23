@echo off
REM build_and_sign_all.bat
REM Check for admin rights and self-elevate if needed
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

REM --- 仮想環境のチェックとセットアップ ---
echo Checking for virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating it...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b %ERRORLEVEL%
    )
    echo Activating virtual environment and installing dependencies...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to activate virtual environment.
        pause
        exit /b %ERRORLEVEL%
    )
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install dependencies from requirements.txt.
            pause
            exit /b %ERRORLEVEL%
        )
    ) else (
        echo Warning: requirements.txt not found. Skipping dependency installation.
    )
) else (
    echo Virtual environment found. Activating it...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to activate virtual environment.
        pause
        exit /b %ERRORLEVEL%
    )
)
REM --- 仮想環境のチェックとセットアップここまで ---

echo Building application with temporary name...
powershell -ExecutionPolicy Bypass -File build_temp.ps1
if %ERRORLEVEL% NEQ 0 (
    echo Build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo Waiting for processes to terminate...
timeout /t 3

echo Copying and signing application...
powershell -ExecutionPolicy Bypass -File copy_and_sign.ps1
if %ERRORLEVEL% NEQ 0 (
    echo Signing failed.
    pause
    exit /b %ERRORLEVEL%
)

echo All processes completed successfully.
pause