# build_temp.ps1
$appName = "MagicalFlyingAlpaca"
$tempName = "TempBuildApp"  # temporary name
$tempPyFile = "mfa_app_temp.py"

# Cleanup
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "temp_build.spec" -Force -ErrorAction SilentlyContinue
Remove-Item -Path $tempPyFile -Force -ErrorAction SilentlyContinue

# Create necessary folders
New-Item -Path "dist" -ItemType Directory -Force | Out-Null

# Read SECRET_KEY from .env file
Write-Host "Reading SECRET_KEY from .env file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found! Please create .env file with SECRET_KEY defined."
    exit 1
}

$secretKey = $null
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*SECRET_KEY\s*=\s*["'']?([^"'']+)["'']?\s*$') {
        $secretKey = $matches[1].Trim()
    }
}

if (-not $secretKey) {
    Write-Error "SECRET_KEY not found in .env file!"
    exit 1
}

Write-Host "SECRET_KEY found in .env file" -ForegroundColor Green

# Create temporary Python file with embedded SECRET_KEY
Write-Host "Creating temporary Python file with embedded SECRET_KEY..." -ForegroundColor Yellow
$pyContent = Get-Content -Path "mfa_app.py" -Raw -Encoding UTF8

# Replace the SECRET_KEY loading section
$pattern = "from dotenv import load_dotenv\r?\nload_dotenv\(\)\r?\nSECRET_KEY = os\.getenv\('SECRET_KEY'\)\r?\nif not SECRET_KEY:\r?\n\s+print\(""ERROR: SECRET_KEY not found in environment variables\.""\)\r?\n\s+print\(""Please ensure \.env file exists with SECRET_KEY defined\.""\)\r?\n\s+sys\.exit\(1\)"
$replacement = "# SECRET_KEY embedded at build time`r`nSECRET_KEY = '$secretKey'"

$modifiedPyContent = $pyContent -replace $pattern, $replacement

# Verify replacement was successful
if ($modifiedPyContent -eq $pyContent) {
    Write-Error "Failed to replace SECRET_KEY loading code!"
    exit 1
}

# UTF-8 without BOM to preserve Japanese characters
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $PWD $tempPyFile), $modifiedPyContent, $utf8NoBom)

# Modify spec file to use temporary Python file
$specContent = Get-Content -Path "mfa_app.spec" -Raw
$modifiedSpec = $specContent -replace "name='$appName'", "name='$tempName'"
$modifiedSpec = $modifiedSpec -replace "'mfa_app\.py'", "'$tempPyFile'"
$modifiedSpec | Out-File -FilePath "temp_build.spec" -Encoding UTF8

Write-Host "Building application with temporary name: $tempName" -ForegroundColor Yellow

# Build with temporary name
pyinstaller --clean temp_build.spec

# Cleanup temporary Python file
Remove-Item -Path $tempPyFile -Force -ErrorAction SilentlyContinue

# Check if build was successful
if (-not (Test-Path "dist\$tempName.exe")) {
    Write-Error "Build failed or EXE file not found"
    exit 1
}

Write-Host "Build completed successfully with temporary name" -ForegroundColor Green
Write-Host "Please run copy_and_sign.ps1 to create the final signed executable" -ForegroundColor Green
