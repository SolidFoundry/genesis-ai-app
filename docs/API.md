# Genesis AI App API 接口文档

## 项目架构概述

Genesis AI App 采用分层架构设计，包含两个主要组件：

### 📁 目录结构
```
apps/
├── mcp_server/          # MCP服务器 - 为其他系统的Agent提供MCP接口
└── rest_api/           # REST API - 为前端和移动端提供HTTP API
```

### 🔧 组件说明
- **MCP Server**: 实现模型上下文协议（Model Context Protocol），为第三方Agent系统提供工具调用接口
- **REST API**: 提供标准的HTTP RESTful接口，支持前端网站和移动应用

---

## REST API 接口

### 🌐 基础信息
- **基础URL**: `http://localhost:8002`
- **API版本**: v1
- **数据格式**: JSON
- **认证方式**: 暂无（生产环境建议添加）

### 📋 接口列表

#### 1. 系统接口

##### 🏠 根路径
- **路径**: `GET /`
- **描述**: 应用基本信息
- **响应示例**:
```json
{
  "message": "Hello World from Genesis AI App!",
  "timestamp": "2025-09-04T10:30:00.000Z",
  "version": "1.0.0"
}
```

##### ❤️ 健康检查
- **路径**: `GET /health`
- **描述**: 检查应用和数据库状态
- **响应示例**:
```json
{
  "status": "ok",
  "message": "Application is running",
  "timestamp": "2025-09-04T10:30:00.000Z",
  "app": {
    "name": "Genesis AI App",
    "version": "1.0.0",
    "environment": "development"
  },
  "database": {
    "status": "healthy",
    "pool": {
      "size": 5,
      "checked_in": 5,
      "checked_out": 0,
      "overflow": 0,
      "invalidated": 0
    }
  }
}
```

#### 2. LLM 工具调用接口

##### 🤖 LLM工具调用（主要接口）
- **路径**: `POST /v1/llm-with-tools`
- **描述**: 主要的AI对话接口，支持工具调用
- **请求体**:
```json
{
  "query": "现在几点了？",
  "session_id": "test-session-123",
  "system_prompt": "你是一个智能助手，可以使用工具来帮助用户",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

- **响应示例**:
```json
{
  "success": true,
  "response": "The current time is 10:56:32 on September 4, 2025.",
  "session_id": "test-session-123",
  "model_used": "qwen-max",
  "usage": {},
  "tools_called": [
    {
      "name": "get_current_datetime",
      "arguments": {}
    }
  ]
}
```

#### 3. 会话管理接口

##### 📝 获取会话历史
- **路径**: `GET /v1/llm-sessions/{session_id}`
- **描述**: 获取指定会话的对话历史
- **响应示例**:
```json
{
  "session_id": "test-session-123",
  "messages": [
    {
      "role": "user",
      "content": "现在几点了？",
      "timestamp": "2025-09-04T10:56:32.000Z"
    },
    {
      "role": "assistant",
      "content": "The current time is 10:56:32 on September 4, 2025.",
      "timestamp": "2025-09-04T10:56:32.000Z"
    }
  ],
  "context": {}
}
```

##### 🗑️ 清除会话历史
- **路径**: `DELETE /v1/llm-sessions/{session_id}`
- **描述**: 清除指定会话的历史记录
- **响应示例**:
```json
{
  "message": "会话历史已清除"
}
```

##### 📋 列出所有会话
- **路径**: `GET /v1/llm-sessions`
- **描述**: 获取所有活跃会话列表
- **响应示例**:
```json
{
  "sessions": ["test-session-123", "session-456"],
  "count": 2
}
```

#### 4. 调试接口

##### 🔧 获取已注册工具
- **路径**: `GET /v1/_debug/tools`
- **描述**: 查看所有可用的AI工具
- **响应示例**:
```json
{
  "count": 6,
  "tools": [
    {
      "name": "calculate",
      "description": "一个安全的计算器，用于执行数学表达式。",
      "parameters": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            "description": "参数: expression"
          }
        },
        "required": ["expression"]
      }
    },
    {
      "name": "get_current_datetime",
      "description": "获取当前服务器的日期和时间。",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  ],
  "raw_schemas": [...]
}
```

##### 🗄️ 数据库状态
- **路径**: `GET /v1/_debug/db-status`
- **描述**: 检查数据库连接状态
- **响应示例**:
```json
{
  "status": "healthy",
  "message": "数据库连接正常",
  "pool_info": {
    "size": 5,
    "checked_in": 5,
    "checked_out": 0,
    "overflow": 0,
    "invalidated": 0
  }
}
```

##### 📊 系统信息
- **路径**: `GET /v1/_debug/system-info`
- **描述**: 获取系统基本信息
- **响应示例**:
```json
{
  "app": {
    "name": "Genesis AI App",
    "version": "1.0.0",
    "status": "running"
  },
  "database": {
    "status": "connected",
    "pool_info": {
      "size": 5,
      "checked_in": 5,
      "checked_out": 0
    }
  },
  "features": [
    "FastAPI REST API",
    "SQLAlchemy ORM",
    "Async Database Connection",
    "Dependency Injection"
  ]
}
```

---

## 🛠️ 可用工具列表

### 当前已注册的AI工具：

1. **get_current_datetime** - 获取当前时间
2. **get_current_weather** - 获取天气信息
3. **calculate** - 数学计算器
4. **get_system_info** - 获取系统信息
5. **search_web** - 网络搜索（模拟）

---

## 📝 使用示例

### 基本对话
```bash
curl -X POST "http://localhost:8002/v1/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "现在几点了？",
    "session_id": "my-session",
    "system_prompt": "你是一个智能助手"
  }'
```

### 数学计算
```bash
curl -X POST "http://localhost:8002/v1/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "计算 15 * 8 + 32",
    "session_id": "calc-session",
    "system_prompt": "你是一个数学助手"
  }'
```

### 查看会话历史
```bash
curl "http://localhost:8002/v1/llm-sessions/my-session"
```

---

## 🔧 开发和测试

### 启动服务
```bash
# 开发模式
make run

# 生产模式
make run-prod

# 自动初始化数据库
python run.py --auto-init
```

### API文档
- **Swagger UI**: `http://localhost:8002/docs`
- **ReDoc**: `http://localhost:8002/redoc`
- **OpenAPI Schema**: `http://localhost:8002/openapi.json`

### 测试工具
- **调试端点**: `http://localhost:8002/v1/_debug/tools`
- **健康检查**: `http://localhost:8002/health`

---

## 📊 性能监控

所有API请求都会自动记录：
- 请求ID追踪
- 响应时间监控
- 详细的操作日志
- 工具调用统计

---

## 🚀 部署说明

### 环境要求
- Python 3.8+
- PostgreSQL 12+
- Redis (可选，用于缓存)

### 配置文件
- `.env` - 环境变量配置
- `logging_config.yaml` - 日志配置
- `pyproject.toml` - 项目依赖

### Docker部署
```bash
docker-compose up -d
```

---

## 📋 更新日志

### v1.0.0 (2025-09-04)
- ✅ 实现LLM工具调用功能
- ✅ 添加会话管理
- ✅ 集成多种AI工具
- ✅ 完善调试接口
- ✅ 优化API路径结构
- ✅ 清理无用接口