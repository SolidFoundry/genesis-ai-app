# Genesis AI 应用数据库设置指南
=================================

本指南将帮助您设置 PostgreSQL 数据库并启动 Genesis AI 应用。

## 前提条件

1. **Docker Desktop** - 确保已安装并启动 Docker Desktop
2. **Python 3.11+** - 确保 Python 已安装
3. **Poetry** - 依赖管理工具

## 快速开始

### 方法一：自动设置（推荐）

1. **运行数据库设置脚本**
   ```bash
   python scripts/setup_db.py
   ```

2. **启动应用**
   ```bash
   python run.py --auto-init
   ```
   或
   ```bash
   start.bat
   ```

### 方法二：手动设置

#### 1. 启动 PostgreSQL 数据库

```bash
# 创建并启动 PostgreSQL 容器
docker run --name genesis-postgres \
  -e POSTGRES_USER=genesis \
  -e POSTGRES_PASSWORD=genesis_password \
  -e POSTGRES_DB=genesis_db \
  -p 5432:5432 \
  -d postgres:15
```

#### 2. 验证数据库连接

```bash
# 测试数据库连接
python scripts/test_postgres.py
```

#### 3. 初始化数据库

```bash
# 创建数据库表结构
python scripts/init_db.py

# 插入示例数据
python scripts/init_sample.py
```

#### 4. 启动应用

```bash
# 启动应用
python run.py --reload
```

## 环境配置

### .env 文件配置

确保 `.env` 文件包含以下配置：

```env
# === Database Configuration ===
DATABASE_USER=genesis
DATABASE_PASSWORD=genesis_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=genesis_db
DATABASE__POOL_SIZE=20
DATABASE__MAX_OVERFLOW=30
DATABASE__POOL_TIMEOUT=30
DATABASE__POOL_RECYCLE=3600
DATABASE__ECHO=false
```

### Docker Compose 配置

使用 Docker Compose 可以更方便地管理服务：

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 数据库结构

### 主要数据表

1. **user_sessions** - 用户会话信息
2. **user_behaviors** - 用户行为记录
3. **intent_analyses** - 意图分析结果
4. **ad_recommendations** - 广告推荐数据
5. **chat_sessions** - 聊天会话信息
6. **chat_messages** - 聊天消息记录
7. **system_config** - 系统配置
8. **llm_calls** - LLM 调用记录
9. **api_logs** - API 日志记录

### 数据模型详情

所有数据模型都定义在 `src/genesis/infrastructure/database/models.py` 文件中，包含完整的字段定义和关系。

## 故障排除

### 常见问题

1. **数据库连接失败**
   ```
   password authentication failed for user "genesis"
   ```
   - 确保 PostgreSQL 容器正在运行
   - 检查用户名和密码是否正确
   - 验证端口映射是否正确

2. **端口被占用**
   ```
   port 5432 is already allocated
   ```
   - 停止占用端口的其他服务
   - 或修改 Docker 端口映射：`-p 5433:5432`

3. **Docker Desktop 未启动**
   - 启动 Docker Desktop
   - 等待完全启动后再运行命令

### 调试命令

```bash
# 查看 Docker 容器状态
docker ps -a

# 查看 PostgreSQL 容器日志
docker logs genesis-postgres

# 进入 PostgreSQL 容器
docker exec -it genesis-postgres psql -U genesis -d genesis_db

# 测试网络连接
telnet localhost 5432
```

## 开发环境设置

### 使用 VS Code

1. 安装 Python 扩展
2. 安装 Docker 扩展
3. 配置 launch.json 进行调试

### 使用 PyCharm

1. 配置 Python 解释器
2. 设置 Docker Compose 运行配置
3. 配置数据库连接

## 生产环境部署

### 安全配置

1. **修改默认密码**
   ```env
   DATABASE_PASSWORD=your_secure_password
   ```

2. **使用环境变量**
   ```bash
   export DATABASE_PASSWORD=$(openssl rand -base64 32)
   ```

3. **网络配置**
   - 使用 Docker 网络
   - 配置防火墙规则
   - 使用 SSL 连接

### 备份和恢复

```bash
# 备份数据库
docker exec genesis-postgres pg_dump -U genesis genesis_db > backup.sql

# 恢复数据库
docker exec -i genesis-postgres psql -U genesis genesis_db < backup.sql
```

## 性能优化

### 数据库优化

1. **连接池配置**
   ```env
   DATABASE__POOL_SIZE=20
   DATABASE__MAX_OVERFLOW=30
   ```

2. **索引优化**
   - 确保常用查询字段有索引
   - 定期分析查询性能

3. **监控**
   - 使用 `docker stats` 监控资源使用
   - 配置数据库慢查询日志

## 支持

如果遇到问题，请检查：

1. Docker Desktop 是否正在运行
2. 端口 5432 是否可用
3. 环境变量配置是否正确
4. 容器日志是否有错误信息

运行 `python scripts/setup_db.py` 可以自动诊断和修复常见问题。