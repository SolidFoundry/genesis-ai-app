# Genesis AI 应用 Makefile
# ========================
# 
# 提供便捷的项目管理命令，包括开发、测试、部署等功能。
# 
# 使用方式：
#   make run          # 启动开发服务器
#   make test         # 运行测试
#   make lint         # 代码检查
#   make format       # 代码格式化
#   make build        # 构建项目
#   make deploy       # 部署项目
#   make clean        # 清理临时文件

# 项目配置
PROJECT_NAME := genesis-ai-app
PYTHON := python
POETRY := poetry
VENV_PATH := .venv

# 颜色定义
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
BOLD := \033[1m
RESET := \033[0m

# 帮助信息
.PHONY: help
help: ## 显示帮助信息
	@echo "$(BOLD)$(PURPLE)Genesis AI 应用项目管理$(RESET)"
	@echo "$(BLUE)======================================$(RESET)"
	@echo ""
	@echo "$(GREEN)可用的命令:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)示例用法:$(RESET)"
	@echo "  make run           # 启动开发服务器"
	@echo "  make test          # 运行测试"
	@echo "  make lint          # 代码检查"
	@echo "  make format        # 代码格式化"
	@echo ""

# 开发环境设置
.PHONY: setup
setup: ## 设置开发环境
	@echo "$(GREEN)🔧 设置开发环境...$(RESET)"
	$(POETRY) install
	@echo "$(GREEN)✅ 开发环境设置完成！$(RESET)"

# 虚拟环境管理
.PHONY: venv
venv: ## 激活虚拟环境
	@echo "$(GREEN)🐍 激活虚拟环境...$(RESET)"
	@echo "$(YELLOW)请运行以下命令激活虚拟环境:$(RESET)"
	@echo "$(CYAN)source $(VENV_PATH)/bin/activate$(RESET)"
	@echo "$(CYAN)或者直接使用 poetry shell$(RESET)"

# 运行应用
.PHONY: run
run: ## 启动开发服务器
	@echo "$(GREEN)🚀 启动开发服务器...$(RESET)"
	$(PYTHON) run.py --reload

# 生产环境运行
.PHONY: run-prod
run-prod: ## 启动生产服务器
	@echo "$(GREEN)🚀 启动生产服务器...$(RESET)"
	$(PYTHON) run.py --env production --workers 4

# 测试相关
.PHONY: test
test: ## 运行所有测试
	@echo "$(GREEN)🧪 运行测试...$(RESET)"
	$(POETRY) run pytest

.PHONY: test-unit
test-unit: ## 运行单元测试
	@echo "$(GREEN)🧪 运行单元测试...$(RESET)"
	$(POETRY) run pytest tests/unit

.PHONY: test-integration
test-integration: ## 运行集成测试
	@echo "$(GREEN)🧪 运行集成测试...$(RESET)"
	$(POETRY) run pytest tests/integration

.PHONY: test-e2e
test-e2e: ## 运行端到端测试
	@echo "$(GREEN)🧪 运行端到端测试...$(RESET)"
	$(POETRY) run pytest tests/e2e

.PHONY: test-coverage
test-coverage: ## 运行测试覆盖率检查
	@echo "$(GREEN)🧪 运行测试覆盖率检查...$(RESET)"
	$(POETRY) run pytest --cov=src --cov-report=html --cov-report=term

# 代码质量
.PHONY: lint
lint: ## 代码检查
	@echo "$(GREEN)🔍 代码检查...$(RESET)"
	$(POETRY) run ruff check src/
	$(POETRY) run mypy src/

.PHONY: format
format: ## 代码格式化
	@echo "$(GREEN)✨ 代码格式化...$(RESET)"
	$(POETRY) run black src/
	$(POETRY) run ruff check --fix src/

.PHONY: format-check
format-check: ## 检查代码格式
	@echo "$(GREEN)🔍 检查代码格式...$(RESET)"
	$(POETRY) run black --check src/
	$(POETRY) run ruff check src/

# 安全检查
.PHONY: security
security: ## 安全检查
	@echo "$(GREEN)🔒 安全检查...$(RESET)"
	@echo "$(YELLOW)注意：需要先安装 bandit$(RESET)"
	$(POETRY) run bandit -r src/

# 依赖管理
.PHONY: install
install: ## 安装依赖
	@echo "$(GREEN)📦 安装依赖...$(RESET)"
	$(POETRY) install

.PHONY: install-dev
install-dev: ## 安装开发依赖
	@echo "$(GREEN)📦 安装开发依赖...$(RESET)"
	$(POETRY) install --with dev

.PHONY: update
update: ## 更新依赖
	@echo "$(GREEN)🔄 更新依赖...$(RESET)"
	$(POETRY) update

.PHONY: lock
lock: ## 生成依赖锁定文件
	@echo "$(GREEN)🔒 生成依赖锁定文件...$(RESET)"
	$(POETRY) lock

# 数据库相关
.PHONY: db-migrate
db-migrate: ## 运行数据库迁移
	@echo "$(GREEN)🗄️ 运行数据库迁移...$(RESET)"
	$(POETRY) run alembic upgrade head

.PHONY: db-downgrade
db-downgrade: ## 回滚数据库迁移
	@echo "$(GREEN)🗄️ 回滚数据库迁移...$(RESET)"
	$(POETRY) run alembic downgrade -1

.PHONY: db-revision
db-revision: ## 创建数据库迁移
	@echo "$(GREEN)🗄️ 创建数据库迁移...$(RESET)"
	@read -p "请输入迁移描述: " desc; \
	$(POETRY) run alembic revision --autogenerate -m "$$desc"

.PHONY: db-clean
db-clean: ## 清理数据库中的测试数据
	@echo "$(GREEN)🗄️ 清理数据库中的测试数据...$(RESET)"
	$(PYTHON) clean_database_auto.py

.PHONY: db-clean-all
db-clean-all: ## 清理数据库中的所有聊天数据
	@echo "$(RED)🗄️ 清理数据库中的所有聊天数据...$(RESET)"
	@echo "$(RED)警告：这将删除所有聊天会话和消息！$(RESET)"
	@read -p "确定要继续吗？(y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		$(PYTHON) clean_database.py; \
	else \
		echo "$(YELLOW)取消清理$(RESET)"; \
	fi

# MCP 服务器管理
.PHONY: mcp-start
mcp-start: ## 启动 MCP 服务器
	@echo "$(GREEN)🚀 启动 MCP 服务器...$(RESET)"
	@echo "$(BLUE)服务地址: http://localhost:8888$(RESET)"
	@echo "$(BLUE)按 Ctrl+C 停止服务$(RESET)"
	MCP_PORT=8888 $(POETRY) run python -m apps.mcp_server.main

.PHONY: mcp-start-fastmcp
mcp-start-fastmcp: ## 使用 FastMCP 标准方式启动 MCP 服务器
	@echo "$(GREEN)🚀 使用 FastMCP 标准方式启动 MCP 服务器...$(RESET)"
	@echo "$(BLUE)服务地址: http://localhost:8001$(RESET)"
	@echo "$(BLUE)按 Ctrl+C 停止服务$(RESET)"
	$(POETRY) run fastmcp run mcp_server_simple.py:mcp --transport http --port 8001

.PHONY: mcp-stop
mcp-stop: ## 停止 MCP 服务器
	@echo "$(GREEN)🛑 停止 MCP 服务器...$(RESET)"
	@if [ -f "mcp_server.pid" ]; then \
		./scripts/mcp_stop.sh; \
	else \
		echo "$(YELLOW)MCP 服务器未运行$(RESET)"; \
	fi

.PHONY: mcp-status
mcp-status: ## 检查 MCP 服务器状态
	@echo "$(BLUE)📊 检查 MCP 服务器状态...$(RESET)"
	@if [ -f "mcp_server.pid" ]; then \
		echo "$(GREEN)✅ MCP 服务器正在运行$(RESET)"; \
		echo "$(BLUE)PID: $$(cat mcp_server.pid)$(RESET)"; \
	else \
		echo "$(RED)❌ MCP 服务器未运行$(RESET)"; \
	fi

.PHONY: mcp-logs
mcp-logs: ## 查看 MCP 服务器日志
	@echo "$(BLUE)📋 查看 MCP 服务器日志...$(RESET)"
	@if [ -f "logs/mcp_server.log" ]; then \
		tail -f logs/mcp_server.log; \
	else \
		echo "$(YELLOW)日志文件不存在$(RESET)"; \
	fi

# 文档生成
.PHONY: docs
docs: ## 生成文档
	@echo "$(GREEN)📚 生成文档...$(RESET)"
	@echo "$(YELLOW)文档生成功能待实现$(RESET)"

# 构建和部署
.PHONY: build
build: ## 构建项目
	@echo "$(GREEN)🔨 构建项目...$(RESET)"
	$(POETRY) build

.PHONY: deploy
deploy: ## 部署项目
	@echo "$(GREEN)🚀 部署项目...$(RESET)"
	@echo "$(YELLOW)部署功能待实现$(RESET)"

# 清理
.PHONY: clean
clean: ## 清理临时文件
	@echo "$(GREEN)🧹 清理临时文件...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	@echo "$(GREEN)✅ 清理完成！$(RESET)"

.PHONY: clean-all
clean-all: ## 深度清理（包括虚拟环境）
	@echo "$(RED)🧹 深度清理...$(RESET)"
	@echo "$(RED)警告：这将删除虚拟环境和所有依赖！$(RESET)"
	@read -p "确定要继续吗？(y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		make clean; \
		rm -rf $(VENV_PATH); \
		rm -rf poetry.lock; \
		echo "$(GREEN)✅ 深度清理完成！$(RESET)"; \
	else \
		echo "$(YELLOW)取消清理$(RESET)"; \
	fi

# 开发工具
.PHONY: shell
shell: ## 启动 Python shell
	@echo "$(GREEN)🐍 启动 Python shell...$(RESET)"
	$(POETRY) run python

.PHONY: ipython
ipython: ## 启动 IPython shell
	@echo "$(GREEN)🐍 启动 IPython shell...$(RESET)"
	$(POETRY) run ipython

# 健康检查
.PHONY: health
health: ## 检查服务健康状态
	@echo "$(GREEN)💚 检查服务健康状态...$(RESET)"
	@curl -s http://localhost:8000/health | jq . || echo "服务未运行"

# 日志查看
.PHONY: logs
logs: ## 查看应用日志
	@echo "$(GREEN)📋 查看应用日志...$(RESET)"
	@echo "$(YELLOW)日志查看功能待实现$(RESET)"

# 开发环境完整设置
.PHONY: dev-setup
dev-setup: setup install-dev ## 完整的开发环境设置
	@echo "$(GREEN)🎉 开发环境设置完成！$(RESET)"
	@echo "$(YELLOW)现在可以运行 'make run' 启动开发服务器$(RESET)"

# 默认目标
.DEFAULT_GOAL := help

# 确保所有命令在项目根目录执行
Makefile: ;
%: Makefile

# 防止 Make 将变量作为命令
.SHELLFLAGS = -ec

# 显示 Make 版本
.PHONY: version
version: ## 显示 Make 版本
	@echo "$(BLUE)Make 版本:$(RESET)"
	@make --version