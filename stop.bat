@echo off
setlocal enabledelayedexpansion

echo Genesis AI App Stopper
echo =====================

echo Current directory: %CD%
echo.

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

echo Using port: !PORT!
echo.

echo Stopping Genesis AI Application on port !PORT!...
echo.

REM Find and kill processes running on the specified port
echo Checking for processes on port !PORT!...
netstat -aon | findstr :!PORT! | findstr LISTENING >nul
if !errorlevel! equ 0 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :!PORT! ^| findstr LISTENING') do (
        echo Found process running on port !PORT!: PID %%a
        echo Terminating process...
        taskkill /F /PID %%a
        if !errorlevel! equ 0 (
            echo Process terminated successfully
        ) else (
            echo Failed to terminate process
        )
    )
) else (
    echo No processes found listening on port !PORT!
)

REM Also check for uvicorn processes specifically
echo.
echo Checking for Uvicorn processes...
tasklist | findstr uvicorn >nul
if !errorlevel! equ 0 (
    for /f "tokens=2" %%p in ('tasklist ^| findstr uvicorn') do (
        echo Found Uvicorn process: %%p
        taskkill /F /PID %%p >nul 2>&1
        if !errorlevel! equ 0 (
            echo Uvicorn process terminated successfully
        ) else (
            echo Failed to terminate Uvicorn process
        )
    )
) else (
    echo No Uvicorn processes found
)

REM Also check for Python processes that might be running our app
echo.
echo Checking for Python processes...
tasklist | findstr python.exe >nul
if !errorlevel! equ 0 (
    for /f "tokens=2" %%p in ('tasklist ^| findstr python.exe') do (
        echo Found Python process: %%p
        REM Check if this python process is using our port
        netstat -aon | findstr :!PORT! | findstr %%p >nul
        if !errorlevel! equ 0 (
            echo Python process %%p is using port !PORT!, terminating...
            taskkill /F /PID %%p >nul 2>&1
            if !errorlevel! equ 0 (
                echo Python process terminated successfully
            ) else (
                echo Failed to terminate Python process
            )
        ) else (
            echo Python process %%p is not using our port, skipping
        )
    )
) else (
    echo No Python processes found
)

REM Check if port is still in use
echo.
echo Checking if port !PORT! is still in use...
timeout /t 2 /nobreak >nul
netstat -aon | findstr :!PORT! | findstr LISTENING >nul
if !errorlevel! equ 0 (
    echo Port !PORT! is still in use
    echo Some processes may still be running
) else (
    echo Port !PORT! is now free
)

echo.
echo Stop process completed
echo If the application is still running, you may need to manually close the command window
echo Window will close automatically...
timeout /t 3 /nobreak >nul