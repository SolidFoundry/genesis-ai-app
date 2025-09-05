-- Genesis AI 应用数据库初始化脚本
-- ===================================
-- 
-- 本脚本创建应用所需的所有数据库表结构
-- 支持PostgreSQL数据库

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表（如果需要用户管理）
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建会话表（用于聊天会话管理）
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    system_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content JSONB NOT NULL,
    message_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (session_id, created_at),
    INDEX (role, created_at)
);

-- 创建LLM调用记录表
CREATE TABLE IF NOT EXISTS llm_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id) ON DELETE SET NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    tokens_used INTEGER DEFAULT 0,
    duration_ms INTEGER,
    cost DECIMAL(10, 6),
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'error', 'timeout')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (session_id, created_at),
    INDEX (provider, status),
    INDEX (created_at)
);

-- 创建API请求日志表
CREATE TABLE IF NOT EXISTS api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    method VARCHAR(10) NOT NULL,
    url VARCHAR(500) NOT NULL,
    status_code INTEGER,
    user_agent TEXT,
    remote_addr VARCHAR(45),
    duration_ms INTEGER,
    request_body JSONB,
    response_body JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (request_id),
    INDEX (method, status_code),
    INDEX (created_at),
    INDEX (remote_addr)
);

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建工具调用记录表
CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id) ON DELETE SET NULL,
    tool_name VARCHAR(100) NOT NULL,
    tool_args JSONB,
    result JSONB,
    duration_ms INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'error')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (session_id, created_at),
    INDEX (tool_name, status),
    INDEX (created_at)
);

-- 创建性能监控表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 6) NOT NULL,
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (metric_name, timestamp),
    INDEX (timestamp)
);

-- 创建错误日志表
CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_id VARCHAR(100),
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (error_type, created_at),
    INDEX (request_id),
    INDEX (created_at)
);

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX (action, resource_type, created_at),
    INDEX (user_id, created_at),
    INDEX (resource_id, created_at)
);

-- 创建触发器函数：自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加 updated_at 触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建视图：会话统计
CREATE OR REPLACE VIEW session_stats AS
SELECT 
    cs.session_id,
    cs.created_at as session_created_at,
    COUNT(cm.id) as message_count,
    MAX(cm.created_at) as last_message_at,
    COUNT(DISTINCT CASE WHEN cm.role = 'user' THEN cm.id END) as user_message_count,
    COUNT(DISTINCT CASE WHEN cm.role = 'assistant' THEN cm.id END) as assistant_message_count
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
GROUP BY cs.session_id, cs.created_at;

-- 创建视图：LLM调用统计
CREATE OR REPLACE VIEW llm_stats AS
SELECT 
    provider,
    model,
    COUNT(id) as total_calls,
    COUNT(CASE WHEN status = 'success' THEN id END) as success_calls,
    COUNT(CASE WHEN status = 'error' THEN id END) as error_calls,
    AVG(duration_ms) as avg_duration_ms,
    SUM(tokens_used) as total_tokens_used,
    SUM(cost) as total_cost,
    MIN(created_at) as first_call_at,
    MAX(created_at) as last_call_at
FROM llm_calls
GROUP BY provider, model;

-- 创建视图：API请求统计
CREATE OR REPLACE VIEW api_stats AS
SELECT 
    method,
    status_code,
    COUNT(id) as request_count,
    AVG(duration_ms) as avg_duration_ms,
    MIN(duration_ms) as min_duration_ms,
    MAX(duration_ms) as max_duration_ms,
    COUNT(CASE WHEN status_code >= 400 THEN id END) as error_count
FROM api_logs
GROUP BY method, status_code;

-- 插入默认系统配置
INSERT INTO system_config (key, value, description) VALUES
('app.name', '"Genesis AI App"', '应用名称'),
('app.version', '"1.0.0"', '应用版本'),
('app.debug', 'false', '调试模式'),
('llm.default_provider', '"openai"', '默认LLM提供商'),
('llm.openai.model', '"gpt-4"', 'OpenAI默认模型'),
('llm.qwen.model', '"qwen-max"', 'Qwen默认模型'),
('logging.level', '"INFO"', '日志级别'),
('logging.max_file_size', '10485760', '日志文件最大大小（字节）'),
('logging.backup_count', '5', '日志备份文件数量')
ON CONFLICT (key) DO NOTHING;

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_calls_session_created ON llm_calls(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_timestamp ON performance_metrics(metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_type_created ON error_logs(error_type, created_at DESC);

-- 添加表注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON TABLE chat_sessions IS '聊天会话表';
COMMENT ON TABLE chat_messages IS '聊天消息表';
COMMENT ON TABLE llm_calls IS 'LLM调用记录表';
COMMENT ON TABLE api_logs IS 'API请求日志表';
COMMENT ON TABLE system_config IS '系统配置表';
COMMENT ON TABLE tool_calls IS '工具调用记录表';
COMMENT ON TABLE performance_metrics IS '性能监控表';
COMMENT ON TABLE error_logs IS '错误日志表';
COMMENT ON TABLE audit_logs IS '审计日志表';

-- 完成提示
DO $$
BEGIN
    RAISE NOTICE '数据库初始化完成！已创建以下表：';
    RAISE NOTICE '- users (用户表)';
    RAISE NOTICE '- chat_sessions (聊天会话表)';
    RAISE NOTICE '- chat_messages (聊天消息表)';
    RAISE NOTICE '- llm_calls (LLM调用记录表)';
    RAISE NOTICE '- api_logs (API请求日志表)';
    RAISE NOTICE '- system_config (系统配置表)';
    RAISE NOTICE '- tool_calls (工具调用记录表)';
    RAISE NOTICE '- performance_metrics (性能监控表)';
    RAISE NOTICE '- error_logs (错误日志表)';
    RAISE NOTICE '- audit_logs (审计日志表)';
    RAISE NOTICE '';
    RAISE NOTICE '已创建以下视图：';
    RAISE NOTICE '- session_stats (会话统计)';
    RAISE NOTICE '- llm_stats (LLM调用统计)';
    RAISE NOTICE '- api_stats (API请求统计)';
END $$;