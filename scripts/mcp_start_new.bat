@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Genesis MCP Server 启动脚本（改进版）
REM =====================================

echo Genesis MCP Server 启动器（改进版）
echo ====================================

REM 切换到项目根目录
cd /d "%~dp0.."
echo 项目目录: %CD%
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python 未找到，请确保Python已安装并在PATH中
    pause
    exit /b 1
)

echo Python 环境检查通过
echo.

REM 设置MCP端口为8888
set MCP_PORT=8888
echo MCP 服务端口: !MCP_PORT!
echo.

REM 创建日志目录
if not exist "logs" mkdir logs

echo 正在启动 MCP 服务器...
echo 服务地址: http://127.0.0.1:!MCP_PORT!/mcp
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 启动MCP服务器
python -m apps.mcp_server.main

if %errorlevel% neq 0 (
    echo.
    echo MCP 服务器已停止（错误代码: %errorlevel%）
) else (
    echo.
    echo MCP 服务器已正常停止
)

echo.
echo 窗口将在3秒后自动关闭...
timeout /t 3 /nobreak >nul