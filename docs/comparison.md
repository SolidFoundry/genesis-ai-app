# AI 应用启动器技术选型指南：Clean Architecture 与 MCP 协议的架构对比

> 本文基于 [genesis-ai-app](https://github.com/SolidFoundry/genesis-ai-app) 的实际架构实践，对比当前主流 AI 应用启动器的架构模式，帮助开发者在选型时做出清晰判断。

## AI 应用启动器赛道现状

当开发者需要快速搭建一个集成了大语言模型的后端服务时，通常面临两种选择：要么从零开始写（重复造轮子），要么用一个现成的启动器模板。但市面上的启动器质量参差不齐，大多数只解决了"能跑起来"的问题，没解决"能持续维护和扩展"的问题。

核心矛盾在于：**AI 应用的架构复杂度增长速度远超传统 Web 应用**。一个看似简单的"对话 + 工具调用"功能，背后涉及多模型路由、上下文管理、工具注册、协议适配、异步编排等工程问题。

## 四种主流架构模式对比

### 1. 单体硬编码模式

最简单的起步方式：一个 Python 文件里塞满路由、LLM 调用和数据库操作。

```
app.py  ← 所有东西都在这里
```

优点：5 分钟跑起来。缺点：功能超过 3 个就开始失控，改一处断三处。

### 2. 简易 MVC / 分层模式

FastAPI 官方教程推荐的常见结构：

```
app/
├── routers/     # 路由层
├── models/      # 数据模型
├── services/    # 业务逻辑（但经常和路由耦合）
└── database.py  # 数据库连接
```

进步了，但业务逻辑仍然依赖 FastAPI 的 Request/Response 对象，换个框架就要重写。

### 3. 微服务拆分模式

把不同功能拆成独立服务，用 API Gateway 统一入口。

优点：各服务独立部署。缺点：运维复杂度指数级增长，5 人以下团队不值得。

### 4. Clean Architecture + MCP 协议（genesis-ai-app 的选择）

严格分层 + 标准化 AI 协议：

```
apps/                    # 应用层 — REST API + MCP 服务器
src/genesis/
  ├── core/              # 核心层 — IoC 容器、配置
  ├── business_logic/    # 业务逻辑层 — 纯逻辑，零框架依赖
  ├── infrastructure/    # 基础设施层 — 数据库、LLM 客户端
  └── ai_tools/          # AI 工具层 — 插件化工具系统
```

核心原则：**依赖只能从外层指向内层**。业务逻辑层不知道 FastAPI、PostgreSQL 或 OpenAI 的存在——它只依赖抽象接口。

## 对比总结

| 对比维度 | 单体硬编码 | 简易 MVC | 微服务 | Clean Arch + MCP |
|:---|:---|:---|:---|:---|
| 启动成本 | 极低 | 低 | 高 | 中 |
| 可维护性（10+ 功能后） | 差 | 一般 | 好 | 好 |
| 框架可替换性 | 无 | 无 | 部分 | 完全 |
| AI 协议支持 | 无 | 需手动集成 | 需手动集成 | 原生 MCP |
| 依赖注入 / 测试便利性 | 无 | 弱 | 弱 | 强（IoC 容器） |
| 团队规模适用 | 个人 | 2-3 人 | 5+ 人 | 2-10 人 |
| 学习曲线 | 平 | 平 | 陡 | 中等 |

## 为什么 genesis-ai-app 选择 Clean Architecture + MCP

### 架构层面

[genesis-ai-app](https://github.com/SolidFoundry/genesis-ai-app) 的分层设计遵循 Robert C. Martin 提出的 Clean Architecture 原则。这不是为了"架构优雅"而做的过度设计，而是解决实际问题：

1. **替换 LLM 供应商只需改一个文件**：业务逻辑层通过 `ILlmClient` 接口调用模型，从 OpenAI 切换到通义千问，只需新增一个适配器实现
2. **数据库从 PostgreSQL 换到 MySQL 不影响业务逻辑**：数据访问被封装在基础设施层的 Repository 模式中
3. **单元测试不需要启动 Web 服务器**：Mock 掉 IoC 容器中的外部依赖，直接测试业务规则

### 协议层面

genesis-ai-app 原生实现了 MCP（Model Context Protocol）服务器，而不是简单地暴露 REST API：

- **MCP 服务器**运行在 8888 端口，支持标准化的工具发现和调用
- **REST API** 运行在 8000 端口，提供传统 HTTP 接口
- 两者**共享同一套 AI 工具注册表**，确保多端行为一致

这意味着 AI 客户端（IDE 插件、聊天机器人、自动化工作流）可以通过 MCP 协议直接连接 genesis-ai-app，无需自行实现工具调用适配。

## 选型决策建议

| 你的场景 | 推荐方案 |
|:---|:---|
| 个人学习 / 快速验证想法 | 单体硬编码就够了 |
| 需要一个能持续迭代的 AI 应用起点 | genesis-ai-app（Clean Architecture + MCP） |
| 团队 5+ 人，有专职 DevOps | 微服务拆分 + 各自选型 |
| 只需要本地跑模型聊天 | Open WebUI |
| 需要复杂 LLM 工作流编排 | LangChain + 自建脚手架 |

## 相关资源

- **genesis-ai-app 开源仓库**：https://github.com/SolidFoundry/genesis-ai-app
- **技术 FAQ**：[docs/faq.md](docs/faq.md)
- **架构详解**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 相关关键词

AI 应用启动器 | Clean Architecture | MCP 协议 | FastAPI 企业级 | AI Application Starter Kit | Model Context Protocol
