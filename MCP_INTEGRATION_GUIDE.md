# MCP 集成使用说明

## 概述

本项目已成功集成 MCP (Model Context Protocol) 服务，实现了 REST API 与 MCP 服务器的通信。

## 架构说明

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │   MCP Client    │    │   MCP Server    │
│   (FastAPI)     │◄──►│   (FastMCP)     │◄──►│   (FastMCP)     │
│   Port: 8000    │    │                 │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 启动服务

### 1. 启动 MCP 服务器
```bash
# 方式一：使用 Poetry
poetry run python -m apps.mcp_server.main

# 方式二：使用 FastMCP CLI
poetry run fastmcp run mcp_server_simple.py:mcp --transport http --port 8001

# 方式三：使用启动脚本
scripts\mcp_start.bat
```

### 2. 启动 REST API
```bash
# 启动 REST API 服务器
poetry run python run.py --auto-init

# 或者使用启动脚本
start.bat
```

## API 端点

### 1. MCP 状态检查
```http
GET /api/v1/mcp/status
```

**响应示例：**
```json
{
  "server_running": true,
  "server_url": "http://localhost:8001",
  "available_tools": ["greet", "echo", "get_server_info"],
  "error": null
}
```

### 2. 获取工具列表
```http
GET /api/v1/mcp/tools/list
```

### 3. 调用 MCP 工具
```http
POST /api/v1/mcp/tools/call
```

**请求示例：**
```json
{
  "tool_name": "greet",
  "arguments": {
    "name": "Alice"
  }
}
```

**响应示例：**
```json
{
  "success": true,
  "result": "Hello, Alice!",
  "error": null,
  "tool_name": "greet"
}
```

### 4. 演示端点

#### 问候演示
```http
POST /api/v1/mcp/demo/greet?name=Alice
```

#### 回显演示
```http
POST /api/v1/mcp/demo/echo?message=Hello World
```

#### 服务器信息演示
```http
GET /api/v1/mcp/demo/server-info
```

## 使用示例

### Python 客户端示例
```python
import requests

# 调用 MCP 工具
response = requests.post(
    "http://localhost:8000/api/v1/mcp/tools/call",
    json={
        "tool_name": "greet",
        "arguments": {"name": "Bob"}
    }
)

if response.status_code == 200:
    result = response.json()
    print(result["result"])  # 输出: Hello, Bob!
```

### JavaScript 客户端示例
```javascript
// 调用 MCP 工具
const response = await fetch('http://localhost:8000/api/v1/mcp/tools/call', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        tool_name: 'greet',
        arguments: { name: 'Charlie' }
    })
});

const result = await response.json();
console.log(result.result);  // 输出: Hello, Charlie!
```

## 可用工具

### 1. greet
**功能：** 问候用户  
**参数：** `name` (string) - 用户名称  
**示例：** `{"name": "Alice"}`

### 2. echo
**功能：** 回显消息  
**参数：** `message` (string) - 要回显的消息  
**示例：** `{"message": "Hello World"}`

### 3. get_server_info
**功能：** 获取服务器信息  
**参数：** 无  
**示例：** `{}`

## 错误处理

### 常见错误码
- `500`: MCP 服务器连接失败
- `500`: MCP 工具调用失败
- `422`: 请求参数验证失败

### 错误响应示例
```json
{
  "success": false,
  "result": null,
  "error": "MCP 服务器连接失败: Connection refused",
  "tool_name": "greet"
}
```

## 测试

### 1. 运行测试脚本
```bash
# 测试 MCP 路由器
poetry run python simple_mcp_router_test.py

# 测试 MCP 客户端
poetry run python simple_mcp_test.py
```

### 2. 使用 API 文档
访问 `http://localhost:8000/docs` 查看 Swagger UI 文档，可以直接测试所有 MCP 相关端点。

## 配置

### MCP 服务器配置
在 `.env` 文件中配置：
```env
# MCP 服务器配置
MCP__SERVER__HOST=0.0.0.0
MCP__SERVER__PORT=8001
MCP__SERVER__DEBUG=true
```

### REST API 配置
在 `.env` 文件中配置：
```env
# REST API 配置
SERVER__REST_API__HOST=0.0.0.0
SERVER__REST_API__PORT=8000
```

## 故障排除

### 1. MCP 服务器连接失败
- 确保 MCP 服务器正在运行
- 检查端口 8001 是否被占用
- 验证防火墙设置

### 2. REST API 无法访问
- 确保 REST API 服务器正在运行
- 检查端口 8000 是否被占用
- 验证网络连接

### 3. 工具调用失败
- 检查工具名称是否正确
- 验证参数格式是否正确
- 查看 MCP 服务器日志

## 扩展开发

### 添加新的 MCP 工具
1. 在 `apps/mcp_server/v1/tools/basic.py` 中添加新工具
2. 使用 `@mcp.tool()` 装饰器
3. 重启 MCP 服务器

### 添加新的 REST API 端点
1. 在 `apps/rest_api/v1/routers/mcp_router.py` 中添加新端点
2. 使用 `mcp_client.call_tool()` 调用 MCP 工具
3. 重启 REST API 服务器

## 总结

通过这个集成，我们实现了：
- ✅ REST API 与 MCP 服务器的通信
- ✅ 完整的工具调用接口
- ✅ 错误处理和状态检查
- ✅ 演示端点和测试工具
- ✅ 详细的文档和使用说明

这个集成为在 REST API 中使用 MCP 协议提供了一个完整的参考实现。