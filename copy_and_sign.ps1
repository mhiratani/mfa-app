# copy_and_sign.ps1
$appName = "MagicalFlyingAlpaca"
$tempName = "TempBuildApp"
$version = "1.0.0"

# Check if temporary file exists
if (-not (Test-Path "dist\$tempName.exe")) {
    Write-Error "Temporary EXE file not found. Please run build_temp.ps1 first."
    exit 1
}

# Final EXE path
$finalExePath = "dist\$appName.exe"

# Remove existing file if present
if (Test-Path $finalExePath) {
    Remove-Item -Path $finalExePath -Force
}

# Copy temporary file
Write-Host "Copying temporary EXE to final name..." -ForegroundColor Yellow
Copy-Item -Path "dist\$tempName.exe" -Destination $finalExePath

# Get code signing certificate
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
if ($null -eq $cert) {
    Write-Error "Code signing certificate not found."
    exit 1
}

# Sign EXE file
Write-Host "Signing EXE file..." -ForegroundColor Yellow
Set-AuthenticodeSignature -FilePath $finalExePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
Write-Host "Successfully signed EXE file" -ForegroundColor Green

# Export certificate (public part only)
$certPath = "dist\$appName-CodeSigningCert.cer"
Export-Certificate -Cert $cert -FilePath $certPath -Type CERT
Write-Host "Exported certificate public part: $certPath" -ForegroundColor Green

# Record build information
$commitHash = git rev-parse --short HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    $commitHash = "unknown"
}

$buildInfo = @"
Application Name: $appName
Version: $version
Build Date/Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Git Commit Hash: $commitHash
Certificate Subject: $($cert.Subject)
Certificate Serial Number: $($cert.SerialNumber)
Certificate Expiry Date: $($cert.NotAfter)
"@

$buildInfoPath = "dist\build_info.txt"
$buildInfo | Out-File $buildInfoPath -Encoding UTF8
Write-Host "Recorded build information: $buildInfoPath" -ForegroundColor Green

# Create and sign installation script
$installScriptContent = @'
# Administrator privilege check
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator"
    Break
}

# Certificate trust setup
$certPath = "$PSScriptRoot\APPNAME-CodeSigningCert.cer"
if (Test-Path $certPath) {
    try {
        Import-Certificate -FilePath $certPath -CertStoreLocation Cert:\LocalMachine\Root -ErrorAction Stop | Out-Null
        Write-Host "Certificate imported to trusted store" -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to import certificate: $_"
        Write-Warning "Skipping certificate trust setup. Warnings may appear."
    }
}
else {
    Write-Warning "Certificate file not found. Skipping certificate trust setup."
}

# Installation directory setup - Changed to AppData\Local
$installDir = "$env:LOCALAPPDATA\APPNAME"
$exeName = "APPNAME.exe"
$sourceExe = "$PSScriptRoot\$exeName"

# Create installation directory
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
    Write-Host "Created installation directory: $installDir"
}

# Copy files
Copy-Item $sourceExe -Destination $installDir
Write-Host "Copied application file"

# Copy build information if exists
$buildInfoPath = "$PSScriptRoot\build_info.txt"
if (Test-Path $buildInfoPath) {
    Copy-Item $buildInfoPath -Destination $installDir
    Write-Host "Copied build information"
}

# Create Start Menu shortcut - Changed to user's Start Menu
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\APPNAME"
if (!(Test-Path $startMenuPath)) {
    New-Item -ItemType Directory -Path $startMenuPath | Out-Null
}

$shortcutPath = "$startMenuPath\APPNAME.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "$installDir\$exeName"
$Shortcut.Save()
Write-Host "Created Start Menu shortcut"

# Create uninstaller
$uninstallScript = @"
# Uninstall script
Remove-Item -Path '$installDir' -Recurse -Force
Remove-Item -Path '$startMenuPath' -Recurse -Force
Write-Host 'Uninstallation completed'
"@

$uninstallScript | Out-File "$installDir\uninstall.ps1" -Encoding UTF8
Write-Host "Created uninstaller"

Write-Host "Installation completed" -ForegroundColor Green
'@ -replace "APPNAME", $appName

# Save installation script
$installScriptPath = "dist\install.ps1"
$installScriptContent | Out-File $installScriptPath -Encoding UTF8
Write-Host "Created installation script: $installScriptPath" -ForegroundColor Green

# Sign installation script
Set-AuthenticodeSignature -FilePath $installScriptPath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
Write-Host "Signed installation script" -ForegroundColor Green

# Create batch file wrapper for install.ps1
$batchContent = @'
@echo off
REM install.bat - PowerShell installation script wrapper

echo APPNAME Installer
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
'@ -replace "APPNAME", $appName

# Save batch file
$batchPath = "dist\install.bat"
$batchContent | Out-File $batchPath -Encoding ASCII
Write-Host "Created batch file wrapper: $batchPath" -ForegroundColor Green

# Sign batch file (optional)
try {
    Set-AuthenticodeSignature -FilePath $batchPath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
    Write-Host "Signed batch file" -ForegroundColor Green
}
catch {
    Write-Warning "Could not sign batch file: $_"
    Write-Warning "Batch files may not support Authenticode signatures on all systems."
}

# Optional: Clean up temporary files
Remove-Item -Path "dist\$tempName.exe" -Force
Remove-Item -Path "temp_build.spec" -Force

Write-Host "Process completed. You can now distribute the files in the dist/ folder." -ForegroundColor Green