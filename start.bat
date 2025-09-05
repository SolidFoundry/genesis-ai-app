@echo off
setlocal enabledelayedexpansion

echo Genesis AI App Launcher
echo =======================

echo Current directory: %CD%
echo.

REM Check if run.py exists
if not exist "run.py" (
    echo ERROR: run.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found
    echo Please run this script from the project root directory
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

REM Extract port number from .env file
set PORT=8000
if exist ".env" (
    echo Reading configuration from .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="SERVER__REST_API__PORT" (
            set PORT=%%b
            echo Found port configuration: !PORT!
        )
    )
)

echo.
echo Checking if port !PORT! is in use...
netstat -ano | findstr ":!PORT!" >nul
if %errorlevel% equ 0 (
    echo Port !PORT! is currently in use.
    echo Attempting to free up the port...
    
    REM Find and kill processes using the port
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":!PORT!"') do (
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
    netstat -ano | findstr ":!PORT!" >nul
    if %errorlevel% equ 0 (
        echo Warning: Port !PORT! is still in use. The application may fail to start.
    ) else (
        echo Port !PORT! is now free.
    )
) else (
    echo Port !PORT! is available.
)

echo.
echo Starting application with auto-initialization...
echo Port: !PORT!
echo Command: poetry run python run.py --port !PORT! --auto-init --reload
echo.
echo Press Ctrl+C to stop the application
echo.

poetry run python run.py --port !PORT! --auto-init --reload

if %errorlevel% neq 0 (
    echo.
    echo Application stopped due to an error
)

echo.
echo Application has stopped
echo Window will close automatically...
timeout /t 3 /nobreak >nul