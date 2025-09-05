@echo off
setlocal enabledelayedexpansion

REM Genesis MCP Server 启动脚本
REM ==========================

chcp 65001 >nul
echo Genesis MCP Server Launcher
echo =============================

echo Current directory: %CD%
echo.

REM Change to project root directory
cd /d "%~dp0.."
echo Changed to project root: %CD%
echo.

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Files found successfully
echo.

REM Check Poetry
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Poetry is not installed or not in PATH
    echo Please install Poetry first
    pause
    exit /b 1
)

echo Poetry is available
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    poetry install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

REM Set MCP port
set MCP_PORT=8001
echo.
echo Checking if port !MCP_PORT! is in use...
netstat -ano | findstr ":!MCP_PORT!" >nul
if %errorlevel% equ 0 (
    echo Port !MCP_PORT! is currently in use.
    echo Attempting to free up the port...
    
    REM Find and kill processes using the port
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":!MCP_PORT!"') do (
        echo Terminating process with PID: %%a
        taskkill /F /PID %%a >nul 2>&1
        if %errorlevel% equ 0 (
            echo Process terminated successfully
        ) else (
            echo Failed to terminate process. It may require elevated privileges.
        )
    )
    
    REM Wait a moment for the port to be freed
    timeout /t 2 /nobreak >nul
    
    REM Check if port is still in use
    netstat -ano | findstr ":!MCP_PORT!" >nul
    if %errorlevel% equ 0 (
        echo Warning: Port !MCP_PORT! is still in use. The application may fail to start.
    ) else (
        echo Port !MCP_PORT! is now free.
    )
) else (
    echo Port !MCP_PORT! is available.
)

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo Starting MCP Server...
echo Port: !MCP_PORT!
echo Command: poetry run python -m apps.mcp_server.main
echo.
echo Press Ctrl+C to stop the server
echo.

poetry run python -m apps.mcp_server.main

if %errorlevel% neq 0 (
    echo.
    echo MCP Server stopped due to an error
)

echo.
echo MCP Server has stopped
echo Window will close automatically...
timeout /t 3 /nobreak >nul