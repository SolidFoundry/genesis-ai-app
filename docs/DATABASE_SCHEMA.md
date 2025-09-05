# Genesis AI App 数据库架构文档

## 概述

本文档描述了 Genesis AI App 的完整数据库架构，确保新开发人员能够成功初始化项目。

## 架构设计原则

1. **统一性**: ORM 模型与 SQL 架构保持一致
2. **完整性**: 包含所有必需的表和关系
3. **可维护性**: 清晰的命名和结构
4. **可扩展性**: 支持未来功能扩展

## 数据库表结构

### 核心表

#### 1. users (用户表)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. user_sessions (用户会话表)
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_segment VARCHAR(100),
    preferences JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. chat_sessions (聊天会话表)
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    system_prompt TEXT,
    user_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. chat_messages (聊天消息表)
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. llm_calls (LLM调用记录表)
```sql
CREATE TABLE llm_calls (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255),
    user_id VARCHAR(255),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    request_data JSON NOT NULL,
    response_data JSON,
    tokens_used INTEGER,
    cost_usd FLOAT,
    latency_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 业务逻辑表

#### 6. user_behaviors (用户行为表)
```sql
CREATE TABLE user_behaviors (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    behavior_type VARCHAR(50) NOT NULL,
    behavior_data JSON NOT NULL,
    detected_intent VARCHAR(255),
    intent_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. intent_analyses (意图分析表)
```sql
CREATE TABLE intent_analyses (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    primary_intent VARCHAR(255) NOT NULL,
    secondary_intents JSON,
    target_audience_segment VARCHAR(100) NOT NULL,
    urgency_level FLOAT NOT NULL,
    analysis_model VARCHAR(100),
    analysis_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. ad_recommendations (广告推荐表)
```sql
CREATE TABLE ad_recommendations (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    analysis_id INTEGER,
    ad_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    relevance_score FLOAT NOT NULL,
    ad_copy TEXT NOT NULL,
    recommendation_reason TEXT,
    position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 系统表

#### 9. system_config (系统配置表)
```sql
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 10. api_logs (API日志表)
```sql
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255),
    user_id VARCHAR(255),
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    query_params JSON,
    headers JSON,
    body TEXT,
    status_code INTEGER NOT NULL,
    response_body TEXT,
    latency_ms INTEGER,
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 监控和运维表

#### 11. tool_calls (工具调用表)
```sql
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255),
    tool_name VARCHAR(100) NOT NULL,
    tool_args JSON,
    result JSON,
    duration_ms INTEGER,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 12. performance_metrics (性能指标表)
```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 6) NOT NULL,
    tags JSON,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 13. error_logs (错误日志表)
```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_id VARCHAR(100),
    context JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 14. audit_logs (审计日志表)
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    user_id VARCHAR(255),
    changes JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 表关系图

```
users
├── user_sessions (1:many)
├── chat_sessions (1:many)
└── audit_logs (1:many)

user_sessions
├── user_behaviors (1:many)
├── intent_analyses (1:many)
└── ad_recommendations (1:many)

chat_sessions
├── chat_messages (1:many)
├── llm_calls (1:many)
├── tool_calls (1:many)
└── api_logs (1:many)

system_config (独立表)
performance_metrics (独立表)
error_logs (独立表)
```

## 初始化流程

### 1. 环境准备
```bash
# 启动数据库
docker-compose up -d

# 安装依赖
make install
```

### 2. 数据库初始化
```bash
# 方法1: 使用ORM模型初始化
python run.py --init-db

# 方法2: 使用SQL脚本初始化
psql -h localhost -U genesis -d genesis_db -f sql/001_initial_schema.sql
```

### 3. 插入示例数据
```bash
# 方法1: 使用ORM脚本
python run.py --init-sample

# 方法2: 使用SQL脚本
psql -h localhost -U genesis -d genesis_db -f sql/002_sample_data.sql
```

### 4. 验证初始化
```bash
# 运行检查脚本
python check_db_structure.py
```

## 开发指南

### 新增表
1. 在 `src/genesis/infrastructure/database/models.py` 中定义ORM模型
2. 在 `sql/` 目录下创建对应的SQL脚本
3. 更新本文档
4. 创建数据库迁移脚本

### 修改表结构
1. 使用Alembic创建迁移
```bash
make db-revision -m "描述变更"
```

2. 应用迁移
```bash
make db-migrate
```

### 数据备份和恢复
```bash
# 备份
pg_dump -h localhost -U genesis -d genesis_db > backup.sql

# 恢复
psql -h localhost -U genesis -d genesis_db < backup.sql
```

## 故障排除

### 常见问题
1. **端口冲突**: 检查 `.env` 文件中的端口配置
2. **数据库连接失败**: 确认PostgreSQL服务正在运行
3. **表已存在错误**: 使用 `ON CONFLICT DO NOTHING` 处理重复数据
4. **权限问题**: 确保数据库用户有创建表的权限

### 调试命令
```bash
# 检查数据库状态
python run.py --db-status

# 查看表结构
python check_db_structure.py

# 清理数据
python scripts/clean_data.py
```

## 安全注意事项

1. **密码加密**: 使用 `bcrypt` 加密用户密码
2. **SQL注入防护**: 使用参数化查询
3. **敏感数据**: 不要在日志中记录敏感信息
4. **访问控制**: 实施适当的数据库权限控制

## 性能优化

1. **索引优化**: 为常用查询字段创建索引
2. **连接池**: 配置适当的数据库连接池
3. **查询优化**: 避免N+1查询问题
4. **定期维护**: 定期清理过期数据