# MCP Server PowerShell Launcher
Write-Host "========================================" -ForegroundColor Green
Write-Host "MCP Server PowerShell Launcher" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Get script directory and change to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
Write-Host "Script directory: $scriptDir" -ForegroundColor Cyan
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Change to project root
Set-Location $projectRoot
Write-Host "Changed to project root: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Check if pyproject.toml exists
if (Test-Path "pyproject.toml") {
    Write-Host "SUCCESS: pyproject.toml found" -ForegroundColor Green
} else {
    Write-Host "ERROR: pyproject.toml not found" -ForegroundColor Red
    Write-Host "Available files:" -ForegroundColor Yellow
    Get-ChildItem -Name
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Poetry
Write-Host "Checking Poetry..." -ForegroundColor Yellow
try {
    poetry --version
    if ($LASTEXITCODE -ne 0) {
        throw "Poetry not found"
    }
    Write-Host "Poetry is available" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Poetry not found or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check virtual environment
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    poetry install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "All checks passed! Ready to start MCP server." -ForegroundColor Green
Write-Host ""

# Ask user if they want to start the server
$response = Read-Host "Do you want to start the MCP server now? (y/N)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Starting MCP Server..." -ForegroundColor Yellow
    Write-Host "Command: poetry run python -m apps.mcp_server.main" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
    Write-Host ""
    
    # Start the server
    poetry run python -m apps.mcp_server.main
} else {
    Write-Host "Server startup cancelled." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script completed." -ForegroundColor Green