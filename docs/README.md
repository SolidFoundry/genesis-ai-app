# Genesis AI App - 接口概览

## 🎯 核心功能
- **LLM工具调用**: 支持大模型+本地工具的智能对话
- **会话管理**: 多轮对话记忆和上下文管理
- **多种AI工具**: 时间、天气、计算器、系统信息等
- **企业级架构**: 清晰的分层设计和依赖注入

## 📡 主要接口

### 系统接口
- `GET /` - 应用信息
- `GET /health` - 健康检查

### LLM接口
- `POST /v1/llm-with-tools` - **主要功能**：AI对话+工具调用
- `GET /v1/llm-sessions` - 会话列表
- `GET /v1/llm-sessions/{id}` - 会话历史
- `DELETE /v1/llm-sessions/{id}` - 清除会话

### 调试接口
- `GET /v1/_debug/tools` - 查看可用工具
- `GET /v1/_debug/db-status` - 数据库状态
- `GET /v1/_debug/system-info` - 系统信息

## 🛠️ 可用工具
1. **get_current_datetime** - 获取当前时间
2. **get_current_weather** - 获取天气信息  
3. **calculate** - 数学计算
4. **get_system_info** - 系统信息
5. **search_web** - 网络搜索

## 🚀 快速开始

```bash
# 启动服务
make run

# 测试工具调用
curl -X POST "http://localhost:8002/v1/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{"query": "现在几点了？", "session_id": "test"}'

# 查看文档
open http://localhost:8002/docs
```

## 📁 项目架构
```
apps/
├── rest_api/     # REST API (前端/移动端)
└── mcp_server/   # MCP服务器 (第三方Agent)
```

## 📖 完整文档
- 详细API文档：[API.md](./API.md)
- 项目配置：[CLAUDE.md](../CLAUDE.md)