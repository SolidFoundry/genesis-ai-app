-- Genesis AI 应用示例数据脚本
-- ==============================
--
-- 本脚本插入示例数据用于测试和演示

-- 插入示例用户
INSERT INTO users (username, email, password_hash, full_name) VALUES
('demo_user', 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', '演示用户'),
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeZeUfkZMBs9kYZP6', '系统管理员')
ON CONFLICT (username) DO NOTHING;

-- 插入示例会话
INSERT INTO chat_sessions (session_id, user_id, system_prompt) VALUES
('session_001', (SELECT id FROM users WHERE username = 'demo_user'), '你是一个专业的AI助手，请帮助用户解决问题。'),
('session_002', (SELECT id FROM users WHERE username = 'demo_user'), '你是一个代码助手，专门帮助用户解决编程问题。'),
('session_003', NULL, '你是一个通用的AI助手，可以回答各种问题。')
ON CONFLICT (session_id) DO NOTHING;

-- 插入示例聊天消息
INSERT INTO chat_messages (session_id, role, content, message_metadata) VALUES
('session_001', 'user', '{"content": "你好，请介绍一下你自己"}', '{"type": "text"}'),
('session_001', 'assistant', '{"content": "你好！我是一个AI助手，可以帮助你回答问题、提供信息、协助编程等。有什么我可以帮助你的吗？"}', '{"type": "text"}'),
('session_001', 'user', '{"content": "你能帮我写一个Python函数来计算斐波那契数列吗？"}', '{"type": "code_request"}'),
('session_001', 'assistant', '{"content": "当然可以！以下是一个计算斐波那契数列的Python函数：\n\n```python\ndef fibonacci(n):\n    \"\"\"计算斐波那契数列的第n项\"\"\"\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# 更高效的迭代版本\ndef fibonacci_iterative(n):\n    \"\"\"使用迭代方法计算斐波那契数列\"\"\"\n    if n <= 1:\n        return n\n    \n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```"}', '{"type": "code"}'),
('session_002', 'user', '{"content": "什么是机器学习？"}', '{"type": "question"}'),
('session_002', 'assistant', '{"content": "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习和改进，而无需明确编程。机器学习算法使用统计方法来识别数据中的模式，然后使用这些模式来做出预测或决策。"}', '{"type": "explanation"}'),
('session_003', 'user', '{"content": "如何优化数据库查询性能？"}', '{"type": "technical_question"}')
ON CONFLICT DO NOTHING;

-- 插入示例LLM调用记录
INSERT INTO llm_calls (session_id, provider, model, prompt, response, tokens_used, duration_ms, status) VALUES
('session_001', 'openai', 'gpt-4', '你好，请介绍一下你自己', '你好！我是一个AI助手，可以帮助你回答问题、提供信息、协助编程等。有什么我可以帮助你的吗？', 45, 1200, 'success'),
('session_001', 'openai', 'gpt-4', '你能帮我写一个Python函数来计算斐波那契数列吗？', '当然可以！以下是一个计算斐波那契数列的Python函数...', 120, 2500, 'success'),
('session_002', 'qwen', 'qwen-max', '什么是机器学习？', '机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习和改进...', 85, 1800, 'success'),
('session_003', 'openai', 'gpt-4', '如何优化数据库查询性能？', '数据库查询性能优化可以从以下几个方面进行：1. 索引优化...', 95, 2200, 'success')
ON CONFLICT DO NOTHING;

-- 插入示例工具调用记录
INSERT INTO tool_calls (session_id, tool_name, tool_args, result, duration_ms, status) VALUES
('session_001', 'calculate', '{"expression": "fibonacci(10)"}', '{"result": "55"}', 150, 'success'),
('session_001', 'calculate', '{"expression": "2 * 3 + 5"}', '{"result": "11"}', 50, 'success'),
('session_002', 'get_weather', '{"city": "Beijing"}', '{"temperature": 25, "weather": "sunny"}', 800, 'success'),
('session_003', 'search_database', '{"query": "SELECT * FROM users LIMIT 5"}', '{"results": [{"id": 1, "username": "demo_user"}, {"id": 2, "username": "admin"}]}', 300, 'success')
ON CONFLICT DO NOTHING;

-- 插入示例API日志
INSERT INTO api_logs (request_id, method, url, status_code, duration_ms, user_agent, remote_addr) VALUES
('req_001', 'GET', '/health', 200, 15, 'Mozilla/5.0', '127.0.0.1'),
('req_002', 'GET', '/api/v1/info', 200, 25, 'Mozilla/5.0', '127.0.0.1'),
('req_003', 'POST', '/v1/_debug/llm-echo', 200, 3500, 'curl/7.68.0', '127.0.0.1'),
('req_004', 'GET', '/v1/_debug/db-status', 200, 50, 'curl/7.68.0', '127.0.0.1'),
('req_005', 'POST', '/v1/_debug/llm-echo', 500, 100, 'curl/7.68.0', '127.0.0.1')
ON CONFLICT (request_id) DO NOTHING;

-- 插入示例性能指标
INSERT INTO performance_metrics (metric_name, metric_value, tags) VALUES
('cpu_usage', 25.5, '{"host": "server1", "environment": "development"}'),
('memory_usage', 512.3, '{"host": "server1", "environment": "development"}'),
('disk_usage', 75.2, '{"host": "server1", "environment": "development"}'),
('active_connections', 15, '{"host": "server1", "environment": "development"}'),
('response_time', 125.5, '{"endpoint": "/health", "method": "GET"}'),
('response_time', 2500.0, '{"endpoint": "/v1/_debug/llm-echo", "method": "POST"}')
ON CONFLICT DO NOTHING;

-- 插入示例错误日志
INSERT INTO error_logs (error_type, error_message, request_id, context) VALUES
('ValueError', 'Invalid input parameter', 'req_005', '{"parameter": "temperature", "value": "invalid"}'),
('ConnectionError', 'Database connection timeout', NULL, '{"timeout": 30, "database": "postgres"}'),
('AuthenticationError', 'Invalid API key', 'req_005', '{"provider": "openai"}')
ON CONFLICT DO NOTHING;

-- 插入示例审计日志
INSERT INTO audit_logs (action, resource_type, resource_id, user_id, changes, ip_address) VALUES
('CREATE', 'chat_session', 'session_001', (SELECT id FROM users WHERE username = 'demo_user'), '{"system_prompt": "你是一个专业的AI助手"}', '127.0.0.1'),
('UPDATE', 'system_config', 'app.debug', (SELECT id FROM users WHERE username = 'admin'), '{"old_value": "false", "new_value": "true"}', '127.0.0.1'),
('DELETE', 'chat_messages', NULL, (SELECT id FROM users WHERE username = 'admin'), '{"deleted_count": 5}', '127.0.0.1')
ON CONFLICT DO NOTHING;

-- 完成提示
DO $$
BEGIN
    RAISE NOTICE '示例数据插入完成！';
    RAISE NOTICE '';
    RAISE NOTICE '已插入：';
    RAISE NOTICE '- 2个用户';
    RAISE NOTICE '- 3个会话';
    RAISE NOTICE '- 6条聊天消息';
    RAISE NOTICE '- 4个LLM调用记录';
    RAISE NOTICE '- 4个工具调用记录';
    RAISE NOTICE '- 5个API日志';
    RAISE NOTICE '- 6个性能指标';
    RAISE NOTICE '- 3个错误日志';
    RAISE NOTICE '- 3个审计日志';
    RAISE NOTICE '';
    RAISE NOTICE '现在可以使用以下凭据测试：';
    RAISE NOTICE '用户名: demo_user, admin';
    RAISE NOTICE '会话ID: session_001, session_002, session_003';
END $$;