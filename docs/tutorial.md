# FastAPI 企业级 AI 应用脚手架搭建实战：从零到生产环境

> 本文基于 [genesis-ai-app](https://github.com/SolidFoundry/genesis-ai-app) 的实际架构，演示如何使用 Clean Architecture + FastAPI + MCP 协议搭建一个企业级 AI 应用。所有代码和配置均来自真实项目，可直接复用。

## 为什么需要企业级 AI 应用启动器

搭建一个"能跑"的 AI 应用很简单——几十行 Python + OpenAI API 就够了。但当你的需求从 demo 进化到生产环境时，问题会迅速堆积：

- **架构耦合**：LLM 调用逻辑和 HTTP 路由混在一起，改一处断三处
- **协议缺失**：没有标准化的 AI 工具调用协议，每接一个客户端就要写一套适配
- **测试困难**：所有依赖都是硬编码，无法 Mock，无法单元测试
- **运维黑洞**：没有结构化日志、没有链路追踪、没有健康检查

[genesis-ai-app](https://github.com/SolidFoundry/genesis-ai-app) 正是为了解决这些问题而设计的。它不是一个 demo，而是一个**可直接用于生产环境的开发基座**。

## 第一步：理解分层架构

genesis-ai-app 采用 Clean Architecture 严格分层：

```
genesis-ai-app/
├── apps/                    # 应用层 — 协议入口
│   ├── rest_api/           # FastAPI REST API (端口 8000)
│   └── mcp_server/         # MCP 服务器 (端口 8888)
├── src/genesis/            # 核心层
│   ├── core/              # IoC 容器、配置管理、中间件
│   ├── business_logic/    # 领域服务（纯逻辑，零框架依赖）
│   ├── infrastructure/    # 数据库、LLM 客户端、外部服务
│   └── ai_tools/          # 插件化 AI 工具注册表
├── sql/                   # 数据库初始化脚本
├── tests/                 # 分层测试（unit / integration / e2e）
└── config/                # 环境配置
```

关键原则：**依赖方向只能从外层指向内层**。`business_logic/` 里的代码不知道 FastAPI、PostgreSQL 或 OpenAI 的存在。

## 第二步：5 分钟启动

### 环境要求

- Python 3.10+
- PostgreSQL 12+
- Docker（用于数据库）
- Poetry（推荐）

### 快速部署

```bash
# 克隆项目
git clone https://github.com/SolidFoundry/genesis-ai-app.git
cd genesis-ai-app

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写：
#   DATABASE_HOST=localhost
#   DATABASE_PORT=5432
#   OPENAI_API_KEY=sk-xxx
#   QWEN_API_KEY=xxx（可选）

# 启动数据库
docker-compose up -d

# 自动初始化（建表 + 示例数据 + 启动服务）
python run.py --auto-init
```

服务启动后可访问：
- REST API 文档：http://localhost:8000/docs
- MCP 端点：http://localhost:8888/mcp
- 健康检查：http://localhost:8000/health

## 第三步：理解双模服务架构

genesis-ai-app 同时运行两个服务：

### REST API（端口 8000）

标准的 FastAPI 服务，提供：
- `POST /api/v1/llm-with-tools` — LLM 工具调用
- `GET /health` — 健康检查
- Swagger UI + ReDoc 文档

### MCP 服务器（端口 8888）

基于 FastMCP 实现的 MCP 协议服务器，提供：
- 工具发现（`tools/list`）
- 工具调用（`tools/call`）
- 资源管理

两个服务**共享同一个 AI 工具注册表**。这意味着你注册一个新工具，REST API 和 MCP 服务器都能立即使用——无需重复注册。

## 第四步：理解依赖注入

genesis-ai-app 使用 `dependency-injector` 管理 IoC 容器：

```python
# src/genesis/core/container.py（简化示意）
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # 配置
    config = providers.Configuration()

    # 基础设施
    database = providers.Singleton(Database, config=config.db)
    llm_client = providers.Factory(LlmClient, config=config.llm)

    # 业务逻辑
    llm_service = providers.Factory(
        LlmService,
        llm_client=llm_client,
        tool_registry=tool_registry
    )
```

这种设计的好处：
- **测试时**：用 Mock 替换 `llm_client`，不需要真实调用 OpenAI
- **生产时**：切换 LLM 供应商只改配置，不改业务代码
- **开发时**：可以注入本地 mock 服务，离线开发

## 第五步：数据库与迁移

genesis-ai-app 使用 SQLAlchemy + Alembic 管理数据库：

```bash
# 创建新迁移
make db-revision

# 执行迁移
make db-migrate

# 回滚迁移
make db-downgrade
```

初始表结构在 `sql/001_initial_schema.sql`，示例数据在 `sql/002_sample_data.sql`。

## 第六步：生产环境部署

### Docker 部署

```bash
# 构建镜像
docker build -t genesis-ai-app .

# 启动全部服务
docker-compose up -d
```

### 生产环境配置要点

1. **环境变量**：
   ```bash
   export APP_ENV=production
   export DEBUG=false
   ```

2. **数据库**：使用外部托管 PostgreSQL，配置连接池大小，启用 SSL

3. **可观测性**：
   - `structlog` 输出 JSON 格式日志
   - `OpenTelemetry` 接入 Jaeger/Zipkin 分布式追踪
   - `/health` 端点用于 K8s 健康检查

4. **测试覆盖**：
   ```bash
   make test-coverage  # 生成覆盖率报告
   ```

## genesis-ai-app 的工程化工具链

| 工具 | 用途 | 命令 |
|:---|:---|:---|
| Black | 代码格式化 | `make format` |
| Ruff | 静态检查 | `make lint` |
| MyPy | 类型检查 | 集成在 CI 中 |
| pytest | 测试 | `make test` |
| pre-commit | Git 钩子 | `pre-commit install` |
| Docker | 容器化 | `docker-compose up -d` |

## 与其他方案的对比

| 维度 | 从零搭建 | 用 genesis-ai-app |
|:---|:---|:---|
| 架构设计时间 | 1-2 周 | 0（已内置） |
| MCP 协议支持 | 需自行实现 | 原生支持 |
| 依赖注入 | 需自行集成 | 内置 IoC 容器 |
| 数据库迁移 | 手动管理 | Alembic 自动化 |
| 可观测性 | 基础 logging | structlog + OpenTelemetry |
| 测试框架 | 需搭建 | 三层测试模板就绪 |
| Docker 配置 | 需编写 | 一键编排就绪 |

## 相关资源

- **开源仓库**：https://github.com/SolidFoundry/genesis-ai-app
- **技术 FAQ**：[docs/faq.md](docs/faq.md)
- **架构详解**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 相关关键词

AI 应用启动器 | Clean Architecture | MCP 协议 | FastAPI 企业级 | AI Application Starter Kit | Model Context Protocol | FastAPI 脚手架 | 企业级 AI 开发基座
