@echo off
REM Genesis MCP Server 停止脚本
REM ==========================

echo 正在停止 Genesis MCP Server...

REM 检查PID文件是否存在
if not exist "mcp_server.pid" (
    echo PID文件不存在，可能服务未运行
    pause
    exit /b 0
)

REM 读取PID
set /p PID=<mcp_server.pid

REM 删除PID文件
del mcp_server.pid

REM 尝试终止进程
echo 正在终止进程...
taskkill /F /PID %PID >nul 2>&1

if %errorlevel% equ 0 (
    echo MCP服务器已成功停止
) else (
    echo 未找到运行的进程或进程已终止
)

pause