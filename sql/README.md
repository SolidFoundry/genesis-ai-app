# Genesis AI 应用数据库脚本
# =========================

本目录包含应用的所有数据库相关脚本。

## 文件说明

### 初始化脚本
- `001_initial_schema.sql` - 数据库表结构初始化脚本
  - 创建所有必要的表结构
  - 设置索引和约束
  - 创建视图和触发器
  - 插入默认系统配置

### 示例数据脚本
- `002_sample_data.sql` - 示例数据插入脚本
  - 插入演示用户和会话
  - 插入示例聊天消息
  - 插入LLM调用记录
  - 插入API日志和性能指标

### 迁移脚本目录
- `migrations/` - 数据库迁移脚本目录
  - 用于版本化的数据库架构变更
  - 遵循命名约定：`YYYYMMDD_HHMMSS_description.sql`

## 数据库表结构

### 核心表
- `users` - 用户表
- `chat_sessions` - 聊天会话表
- `chat_messages` - 聊天消息表
- `llm_calls` - LLM调用记录表

### 监控和日志表
- `api_logs` - API请求日志表
- `tool_calls` - 工具调用记录表
- `performance_metrics` - 性能监控表
- `error_logs` - 错误日志表
- `audit_logs` - 审计日志表

### 配置表
- `system_config` - 系统配置表

### 视图
- `session_stats` - 会话统计视图
- `llm_stats` - LLM调用统计视图
- `api_stats` - API请求统计视图

## 使用方法

### 1. 初始化数据库
```bash
# 连接到PostgreSQL并执行初始化脚本
psql -h localhost -U postgres -d genesis_db -f sql/001_initial_schema.sql
```

### 2. 插入示例数据（可选）
```bash
# 执行示例数据脚本
psql -h localhost -U postgres -d genesis_db -f sql/002_sample_data.sql
```

### 3. 数据库迁移
当需要修改数据库结构时，在 `migrations/` 目录下创建新的迁移脚本：
```bash
# 创建新的迁移脚本
touch sql/migrations/20250903_120000_add_new_feature.sql
```

## 数据库要求

- PostgreSQL 13+
- 需要uuid-ossp扩展
- 建议使用UTF-8编码

## 环境变量配置

确保在 `.env` 文件中正确配置数据库连接：
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/genesis_db
```

## 注意事项

1. **生产环境**：不要在生产环境中执行示例数据脚本
2. **备份数据**：执行数据库变更前请备份数据
3. **权限管理**：确保数据库用户具有适当的权限
4. **测试验证**：执行脚本后请验证数据完整性

## 故障排除

如果遇到以下问题：

### 权限错误
```sql
-- 确保用户具有创建扩展的权限
GRANT ALL PRIVILEGES ON DATABASE genesis_db TO your_user;
```

### UUID扩展不存在
```sql
-- 手动创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 表已存在错误
```sql
-- 脚本使用了 IF NOT EXISTS，应该不会出现此错误
-- 如果出现，可以手动删除表或修改脚本
```