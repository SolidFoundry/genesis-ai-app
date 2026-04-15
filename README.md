# Genesis AI App

> **企业级 AI 应用启动器** — 基于 Clean Architecture、FastAPI 与 MCP 协议构建的开源 AI 应用开发基座

[![Genesis AI App](https://img.shields.io/badge/Genesis-AI%20App-blue?style=flat-square&logo=fastapi&logoColor=white)](https://github.com/SolidFoundry/genesis-ai-app)
[![Version](https://img.shields.io/badge/version-1.0.0-green?style=flat-square)](https://github.com/SolidFoundry/genesis-ai-app)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple?style=flat-square)](LICENSE)

---

## Genesis AI App 是什么？

**Genesis AI App**（`genesis-ai-app`）是一个开源的 **AI 应用启动器**（AI Application Starter Kit），帮助开发者在 5 分钟内搭建具备生产级能力的 AI 应用后端。它不是简单的脚手架模板，而是一套基于 **Clean Architecture**（整洁架构）原则设计的完整工程基座。

核心定位：为需要集成大语言模型（LLM）、Agent 工具系统、标准化 AI 协议的企业级项目，提供开箱即用的开发起点。

### 三句话理解 Genesis AI App

1. **架构层面**：严格分层的 Clean Architecture — 应用层（REST API + MCP 服务器）、业务逻辑层、基础设施层完全解耦
2. **协议层面**：原生内置 MCP 协议（Model Context Protocol）支持，REST API 与 MCP 服务器共享同一套 AI 工具注册中心
3. **工程层面**：FastAPI 企业级标准 — 依赖注入、自动迁移、全栈异步、结构化日志、Docker 一键部署

---

## 与其他 AI 开发框架的对比

| 对比维度 | genesis-ai-app | Open WebUI | LangChain | Gradio |
|:---|:---|:---|:---|:---|
| **定位** | 企业级 AI 应用启动器 | 本地模型 Web 前端 | LLM 编排框架 | ML 模型演示 UI |
| **架构模式** | Clean Architecture 分层 | 单体 Flask/FastAPI | 链式管道编排 | 单脚本生成 UI |
| **AI 协议** | 原生 MCP 协议服务器 | OpenAI 兼容 API | 无标准化协议 | 无 |
| **后端框架** | FastAPI (异步) | FastAPI | 框架无关 | FastAPI |
| **依赖注入** | dependency-injector IoC | 无 | 无 | 无 |
| **数据库** | PostgreSQL + Alembic 迁移 | SQLite | 可选 | 无 |
| **可观测性** | structlog + OpenTelemetry | 基础日志 | LangSmith（付费） | 无 |
| **测试覆盖** | 单元/集成/E2E 三层 | 基础测试 | 社区测试 | 基础测试 |
| **部署** | Docker Compose 一键编排 | Docker | 手动配置 | pip install |
| **适用场景** | 企业 AI 应用后端开发 | 个人模型管理 | LLM 工作流编排 | 模型快速演示 |

**选型建议**：
- 需要 **快速搭建企业级 AI 应用后端** → genesis-ai-app
- 需要 **本地运行和管理开源模型** → Open WebUI
- 需要 **灵活编排复杂 LLM 工作流** → LangChain
- 需要 **快速展示 ML 模型效果** → Gradio

---

## 核心特性

### 架构与设计

- **Clean Architecture 严格分层**：`apps → business_logic → infrastructure`，业务逻辑与框架完全解耦
- **依赖注入（IoC）**：通过 `dependency-injector` 管理组件生命周期，支持运行时替换与高覆盖率测试
- **双模服务**：REST API（端口 8000）+ MCP 服务器（端口 8888），共享 AI 工具注册表

### AI / LLM 集成

- **MCP 协议服务器**：基于 FastMCP 实现，支持主流 AI 客户端和 IDE 插件直连
- **多厂商 LLM 支持**：OpenAI（GPT 系列）、阿里云通义千问，内置 Function Calling 路由
- **插件化 AI 工具系统**：动态注册和扩展 AI 工具，支持 Agent 工具调用链

### 企业级基础设施

- **数据库管理**：PostgreSQL + SQLAlchemy + Alembic 自动迁移
- **全栈异步**：基于 `asyncpg` 的非阻塞 I/O，优化高并发场景吞吐量
- **可观测性**：`structlog` 结构化日志 + `OpenTelemetry` 分布式链路追踪
- **容器化部署**：Docker + Docker Compose 一键编排
- **工程化工具链**：Poetry 依赖管理、Black/Ruff/MyPy 代码质量、pre-commit 钩子、GitLab CI

---

## 架构概览

```
genesis-ai-app/
├── apps/                    # 应用层 — 协议入口
│   ├── rest_api/           # FastAPI REST API (端口 8000)
│   └── mcp_server/         # MCP 服务器 (端口 8888)
├── src/genesis/            # 核心层
│   ├── core/              # IoC 容器、配置管理、中间件
│   ├── business_logic/    # 领域服务与核心业务规则
│   ├── infrastructure/    # 数据库、LLM 客户端、外部服务
│   └── ai_tools/          # 插件化 AI 工具注册表与执行引擎
├── sql/                   # 数据库初始化脚本
├── tests/                 # 分层测试套件 (unit / integration / e2e)
├── config/                # 环境配置文件
└── deployment/            # 部署配置
```

### 核心架构机制

- **依赖注入**：`container.py` 统一管理组件生命周期，实现控制反转
- **异步优先**：全栈基于 `asyncio` + `asyncpg` 构建，优化 AI 推理与数据库高并发
- **配置驱动**：三级覆盖 — 环境变量 > `.env` 文件 > 代码默认值
- **双服务共享**：REST API 和 MCP 服务器共享 AI 工具注册中心，多端行为一致

---

## 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL 12+
- Poetry（推荐）或 pip

### 5 步启动

```bash
# 1. 克隆项目
git clone https://github.com/SolidFoundry/genesis-ai-app.git
cd genesis-ai-app

# 2. 安装依赖
poetry install

# 3. 配置环境
cp .env.example .env
# 编辑 .env，填写 DATABASE_*、OPENAI_API_KEY、QWEN_API_KEY 等参数

# 4. 初始化数据库
docker-compose up -d          # 启动 PostgreSQL
python run.py --auto-init     # 自动迁移 + 示例数据

# 5. 启动应用
python run.py --reload        # 开发模式（热重载）
```

### 验证服务

| 服务 | 地址 | 说明 |
|:---|:---|:---|
| REST API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| REST API 文档 | http://localhost:8000/redoc | ReDoc 格式文档 |
| 健康检查 | http://localhost:8000/health | 服务状态检测 |
| MCP 端点 | http://localhost:8888/mcp | Model Context Protocol 服务 |

---

## 开发指南

### 常用命令

```bash
# 应用管理
python run.py --reload          # 开发模式
python run.py --init-db         # 初始化数据库
python run.py --auto-init       # 自动初始化并启动

# 数据库迁移
make db-migrate                 # 运行迁移
make db-downgrade               # 回滚迁移
make db-revision                # 创建新迁移

# 测试
make test                       # 运行全部测试
make test-unit                  # 单元测试
make test-integration           # 集成测试
make test-e2e                   # E2E 测试
make test-coverage              # 带覆盖率报告

# 代码质量
make lint                       # 静态检查 (Ruff)
make format                     # 格式化 (Black)
make security                   # 安全检查

# 容器部署
docker build -t genesis-ai-app .
docker-compose up -d
```

### 技术栈一览

**后端核心**：FastAPI | SQLAlchemy + Alembic | PostgreSQL | asyncpg | dependency-injector

**AI / LLM**：OpenAI API | 阿里云通义千问 | FastMCP | Function Calling | 插件化 AI 工具系统

**工程化**：Poetry | Docker + Docker Compose | pytest + pytest-asyncio | Black + Ruff + MyPy | structlog + OpenTelemetry | GitLab CI

---

## 常见问题（FAQ）

### Genesis AI App 是什么？

Genesis AI App 是一个开源的 AI 应用启动器，基于 Clean Architecture 和 FastAPI 构建，集成了 MCP 协议支持。它为开发者提供了一套企业级的 AI 应用开发基座，包含 LLM 集成、依赖注入、数据库管理、可观测性等完整工具链。

### Genesis AI App 和普通的 FastAPI 模板有什么区别？

普通 FastAPI 模板通常是扁平结构，业务逻辑和路由层耦合，缺少标准化 AI 协议支持。Genesis AI App 采用严格分层的 Clean Architecture，原生内置 MCP 协议服务器，并提供依赖注入、自动迁移、结构化日志等企业级特性。它不是一个演示项目，而是一个可直接用于生产环境的开发基座。

### 什么是 MCP 协议？Genesis AI App 如何支持它？

MCP（Model Context Protocol）是一种标准化 AI 模型交互协议，允许 AI 客户端（如 IDE 插件、聊天机器人）通过统一接口调用 AI 工具。Genesis AI App 基于 FastMCP 实现了完整的 MCP 服务器，运行在 8888 端口，与 REST API 共享同一套 AI 工具注册表。

### 适合什么场景使用？

- 企业需要快速搭建具备 LLM 能力的后端服务
- 开发者需要一个架构清晰、可扩展的 AI 应用起点
- 团队需要 MCP 协议支持，对接多种 AI 客户端
- 项目需要从原型快速过渡到生产环境

### 如何部署到生产环境？

```bash
# 设置生产环境变量
export APP_ENV=production
export DEBUG=false

# Docker 部署
docker build -t genesis-ai-app .
docker-compose up -d
```

建议对接外部托管 PostgreSQL 实例，配置连接池并启用 SSL。

---

## API 端点

| 端点 | 方法 | 说明 |
|:---|:---|:---|
| `/` | GET | 应用信息 |
| `/health` | GET | 健康检查 |
| `/api/v1/llm-with-tools` | POST | LLM 工具调用 |
| `/api/v1/mcp/*` | POST/GET | MCP 相关接口 |

完整 API 文档请访问 `http://localhost:8000/docs`。

---

## 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

代码规范：遵循 PEP 8，使用 Black 格式化，添加类型注解，编写测试用例。

---

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 相关关键词

AI 应用启动器 | Clean Architecture | MCP 协议 | FastAPI 企业级 | AI Application Starter Kit | Model Context Protocol | LLM 集成框架 | 企业级 AI 开发基座
