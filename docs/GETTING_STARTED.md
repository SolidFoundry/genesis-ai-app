# Genesis AI App 新开发人员快速开始指南

## 🚀 快速开始

### 1. 环境准备

#### 必需软件
- Python 3.8+
- PostgreSQL 12+
- Poetry (依赖管理)
- Docker (可选，用于数据库)

#### 安装步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd genesis-ai-app

# 2. 安装Poetry (如果尚未安装)
curl -sSL https://install.python-poetry.org | python3 -

# 3. 安装依赖
make setup
```

### 2. 数据库设置

#### 方法A：使用Docker (推荐)
```bash
# 启动数据库
docker-compose up -d

# 初始化数据库
python scripts/initialize_complete.py
```

#### 方法B：手动设置
```bash
# 1. 创建PostgreSQL数据库
createdb genesis_db
createuser genesis

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接信息

# 3. 初始化数据库
python scripts/initialize_complete.py
```

### 3. 启动应用

#### REST API 服务
```bash
# 方法1：使用Make命令
make run

# 方法2：直接运行
python run.py --auto-init

# 方法3：使用Windows批处理
start.bat
```

#### MCP 服务
```bash
# 方法1：使用Make命令
make mcp-start

# 方法2：使用启动脚本
./scripts/mcp_start.sh    # Linux/Mac
scripts\mcp_start.bat     # Windows

# 方法3：直接运行
python -m apps.mcp_server.main
```

#### 生产模式
```bash
make run-prod
```

### 4. 验证安装

#### REST API 验证
```bash
# 检查健康状态
curl http://localhost:8002/health

# 查看API文档
open http://localhost:8002/docs
```

#### MCP 服务验证
```bash
# 检查MCP服务状态
make mcp-status

# 测试MCP工具
python scripts/test_mcp_server.py

# 查看MCP服务日志
make mcp-logs
```

#### 运行测试
```bash
make test
```

## 📁 项目结构

```
genesis-ai-app/
├── src/genesis/                 # 核心代码
│   ├── core/                   # 核心服务
│   ├── infrastructure/         # 基础设施
│   │   ├── database/          # 数据库相关
│   │   └── llm/              # LLM集成
│   └── ai_tools/             # AI工具
├── apps/                      # 应用层
│   ├── rest_api/             # REST API服务
│   └── mcp_server/           # MCP服务
│       ├── main.py           # 服务入口
│       ├── config.py         # 配置管理
│       └── v1/               # v1版本API
├── scripts/                   # 脚本文件
├── sql/                      # SQL脚本
├── docs/                     # 文档
├── tests/                    # 测试
└── docker-compose.yml        # Docker配置
```

## 🔧 开发工作流

### 1. 代码质量检查
```bash
# 格式化代码
make format

# 代码检查
make lint

# 类型检查
make type-check
```

### 2. 数据库操作
```bash
# 创建迁移
make db-revision -m "描述变更"

# 应用迁移
make db-migrate

# 回滚迁移
make db-downgrade
```

### 3. 测试
```bash
# 运行所有测试
make test

# 运行特定测试
make test-unit
make test-integration
make test-e2e

# 生成覆盖率报告
make test-coverage
```

## 📚 重要文档

- [数据库架构文档](docs/DATABASE_SCHEMA.md)
- [API文档](http://localhost:8002/docs)
- [CLAUDE.md](CLAUDE.md) - 开发指南
- [README.md](README.md) - 项目概述

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -ano | findstr :8002
   
   # 使用start.bat自动处理端口冲突
   start.bat
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose ps
   
   # 重新初始化数据库
   python scripts/initialize_complete.py
   ```

3. **依赖问题**
   ```bash
   # 重新安装依赖
   make clean
   make install
   ```

### 调试命令
```bash
# 检查数据库状态
python run.py --db-status

# 查看表结构
python check_db_structure.py

# 清理数据
python scripts/clean_data.py
```

## 🎯 下一步

1. 阅读 [数据库架构文档](docs/DATABASE_SCHEMA.md) 了解数据模型
2. 查看 [API文档](http://localhost:8002/docs) 了解可用接口
3. 运行 `make test` 确保环境正常
4. 开始开发你的第一个功能！

## 📞 获取帮助

- 查看项目文档
- 运行 `make help` 获取可用命令
- 联系项目维护者

---

**祝您开发愉快！** 🎉