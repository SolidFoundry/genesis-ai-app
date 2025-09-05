#!/bin/bash
# Genesis MCP Server 启动脚本
# ==========================

echo "正在启动 Genesis MCP Server..."

# 设置环境变量
export PYTHONPATH="$(dirname "$0")/..:$PYTHONPATH"

# 检查PID文件是否存在
if [ -f "mcp_server.pid" ]; then
    echo "警告: PID文件已存在，可能已有服务在运行"
    echo "如果需要重新启动，请先运行 ./scripts/mcp_stop.sh"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动MCP服务器
echo "启动MCP服务器在端口 8001..."
python -m apps.mcp_server.main

echo "MCP服务器已停止"