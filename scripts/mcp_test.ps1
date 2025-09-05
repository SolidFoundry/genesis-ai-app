# MCP Server Test Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "MCP Server PowerShell Test Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:PYTHONPATH = Join-Path $PSScriptRoot ".."
Write-Host "PYTHONPATH: $($env:PYTHONPATH)"
Write-Host ""

# Check Python
Write-Host "Checking Python environment..." -ForegroundColor Yellow
try {
    python --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python environment OK" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found or not configured properly" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check module import
Write-Host "Checking module import..." -ForegroundColor Yellow
try {
    python -c "import apps.mcp_server.main; print('Module import successful')"
    if ($LASTEXITCODE -ne 0) {
        throw "Module import failed"
    }
    Write-Host "Module import OK" -ForegroundColor Green
} catch {
    Write-Host "Error: Module import failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check project structure
Write-Host "Checking project structure..." -ForegroundColor Yellow
$mainPath = Join-Path $PSScriptRoot "..\apps\mcp_server\main.py"
if (Test-Path $mainPath) {
    Write-Host "MCP server main file found: $mainPath" -ForegroundColor Green
} else {
    Write-Host "Error: MCP server main file not found: $mainPath" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check port
Write-Host "Checking port 8001..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr ":8001"
if ($portCheck) {
    Write-Host "Warning: Port 8001 is already in use" -ForegroundColor Yellow
    Write-Host $portCheck
} else {
    Write-Host "Port 8001 is available" -ForegroundColor Green
}
Write-Host ""

# Create logs directory
Write-Host "Creating logs directory..." -ForegroundColor Yellow
$logDir = Join-Path $PSScriptRoot "logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
    Write-Host "Logs directory created" -ForegroundColor Green
} else {
    Write-Host "Logs directory already exists" -ForegroundColor Green
}
Write-Host ""

Write-Host "All checks passed. Ready to start MCP server." -ForegroundColor Green
Write-Host ""

# Ask user if they want to start the server
$response = Read-Host "Do you want to start the MCP server now? (y/N)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Starting MCP server..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
    Write-Host ""
    
    # Start the server
    python -m apps.mcp_server.main
} else {
    Write-Host "Server startup cancelled." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test completed." -ForegroundColor Green