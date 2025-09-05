#!/bin/bash
# Genesis MCP Server 停止脚本
# ==========================

echo "正在停止 Genesis MCP Server..."

# 检查PID文件是否存在
if [ ! -f "mcp_server.pid" ]; then
    echo "PID文件不存在，可能服务未运行"
    exit 0
fi

# 读取PID
PID=$(cat mcp_server.pid)

# 删除PID文件
rm -f mcp_server.pid

# 尝试终止进程
echo "正在终止进程..."
if kill -0 $PID 2>/dev/null; then
    kill -TERM $PID
    sleep 2
    
    # 如果进程仍在运行，强制终止
    if kill -0 $PID 2>/dev/null; then
        kill -KILL $PID
        echo "MCP服务器已强制停止"
    else
        echo "MCP服务器已成功停止"
    fi
else
    echo "进程未运行"
fi