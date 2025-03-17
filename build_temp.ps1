# build_temp.ps1
$appName = "MagicalFlyingAlpaca"
$tempName = "TempBuildApp"  # temporary name

# Cleanup
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "temp_build.spec" -Force -ErrorAction SilentlyContinue

# Create necessary folders
New-Item -Path "dist" -ItemType Directory -Force | Out-Null

# Modify spec file with temporary name
$specContent = Get-Content -Path "mfa_app.spec" -Raw
$modifiedSpec = $specContent -replace "name='$appName'", "name='$tempName'"
$modifiedSpec | Out-File -FilePath "temp_build.spec" -Encoding UTF8

Write-Host "Building application with temporary name: $tempName" -ForegroundColor Yellow

# Build with temporary name
pyinstaller --clean temp_build.spec

# Check if build was successful
if (-not (Test-Path "dist\$tempName.exe")) {
    Write-Error "Build failed or EXE file not found"
    exit 1
}

Write-Host "Build completed successfully with temporary name" -ForegroundColor Green
Write-Host "Please run copy_and_sign.ps1 to create the final signed executable" -ForegroundColor Green