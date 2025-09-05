@echo off
REM Genesis MCP Server 调试启动脚本
REM ==========================

echo ========================================
echo Genesis MCP Server 调试启动脚本
echo ========================================
echo.

REM 显示当前工作目录
echo 当前工作目录: %CD%
echo.

REM 检查Python是否可用
echo 检查Python环境...
".\.venv\Scripts\python" --version
if %errorlevel% neq 0 (
    echo 错误: Python未找到或未正确配置
    pause
    exit /b 1
)
echo Python环境正常
echo.

REM 设置环境变量
echo 设置PYTHONPATH...
set PYTHONPATH=%~dp0..;%PYTHONPATH%
echo PYTHONPATH: %PYTHONPATH%
echo.

REM 检查项目结构
echo 检查项目结构...
if exist "%~dp0..\apps\mcp_server\main.py" (
    echo 找到MCP服务主文件
) else (
    echo 错误: 未找到MCP服务主文件
    echo 期望路径: %~dp0..\apps\mcp_server\main.py
    pause
    exit /b 1
)
echo.

REM 检查端口是否被占用
echo 检查端口8001...
netstat -ano | findstr ":8001"
if %errorlevel% equ 0 (
    echo 警告: 端口8001已被占用
    echo 上面的输出显示了占用该端口的进程
    echo.
) else (
    echo 端口8001可用
)
echo.

REM 创建日志目录
echo 创建日志目录...
if not exist "logs" mkdir logs
echo 日志目录已创建
echo.

REM 检查PID文件
if exist "mcp_server.pid" (
    echo 警告: PID文件已存在
    echo 内容:
    type mcp_server.pid
    echo.
    echo 建议先运行 mcp_stop.bat
    pause
    exit /b 1
)

echo 所有检查通过，准备启动MCP服务器...
echo.
echo ========================================
echo 按任意键启动MCP服务器，或关闭窗口取消...
pause >nul

echo 启动MCP服务器...
echo.

REM 启动服务器
".\.venv\Scripts\python" -m apps.mcp_server.main

echo.
echo ========================================
echo MCP服务器已停止
echo 按任意键退出...
pause >nul