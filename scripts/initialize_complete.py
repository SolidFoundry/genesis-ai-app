#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genesis数据库完整初始化脚本
========================

本脚本确保所有数据库表都能正确创建，包括：
- 从ORM模型创建表
- 从SQL脚本创建表
- 处理表结构差异
- 插入默认数据

使用方法：
    python scripts/initialize_complete.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.genesis.infrastructure.database.manager import Base, DatabaseManager
from src.genesis.infrastructure.database.models import *
from src.genesis.core.settings import settings


async def initialize_complete_database():
    """完整初始化数据库"""
    print("开始完整数据库初始化...")
    
    try:
        # 创建数据库管理器
        db_manager = DatabaseManager(settings.database)
        await db_manager.initialize()
        print("OK - 数据库连接成功")
        
        engine = db_manager.engine
        
        # 步骤1：从ORM模型创建所有表
        print("\n步骤1：从ORM模型创建表...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("OK - ORM模型表创建完成")
        
        # 步骤2：检查和创建额外的表和索引
        print("\n步骤2：检查和创建额外的表结构...")
        await create_additional_tables(engine)
        print("OK - 额外表结构创建完成")
        
        # 步骤3：插入默认配置
        print("\n步骤3：插入默认配置...")
        await insert_default_config(engine)
        print("OK - 默认配置插入完成")
        
        # 步骤4：验证所有表
        print("\n步骤4：验证所有表...")
        await verify_all_tables(engine)
        print("OK - 所有表验证完成")
        
        # 步骤5：显示初始化结果
        print("\n步骤5：显示初始化结果...")
        await show_initialization_summary(engine)
        
        await db_manager.close()
        
        print("\nOK - 数据库初始化完成！")
        print("\n新开发人员现在可以：")
        print("1. 运行 'python run.py --auto-init' 启动应用")
        print("2. 运行 'make run' 启动开发服务器")
        print("3. 访问 'http://localhost:8002/docs' 查看API文档")
        
        return True
        
    except Exception as e:
        print(f"ERROR - 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def create_additional_tables(engine):
    """创建额外的表结构"""
    async with engine.begin() as conn:
        # 启用PostgreSQL扩展
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        
        # 创建触发器函数
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """))
        
        # 为需要的表添加updated_at触发器
        tables_with_updated_at = [
            "users", "chat_sessions", "system_config"
        ]
        
        for table in tables_with_updated_at:
            # 先检查触发器是否存在
            result = await conn.execute(text("""
                SELECT 1 FROM information_schema.triggers 
                WHERE trigger_name = :trigger_name
            """), {"trigger_name": f"update_{table}_updated_at"})
            
            if not result.fetchone():
                await conn.execute(text(f"""
                    CREATE TRIGGER update_{table}_updated_at 
                    BEFORE UPDATE ON {table}
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
                """))
        
        # 创建视图
        await create_views(conn)
        
        # 创建优化索引
        await create_optimization_indexes(conn)


async def create_views(conn):
    """创建数据库视图"""
    # 会话统计视图
    await conn.execute(text("""
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
        GROUP BY cs.session_id, cs.created_at
    """))
    
    # LLM调用统计视图
    await conn.execute(text("""
        CREATE OR REPLACE VIEW llm_stats AS
        SELECT 
            provider,
            model,
            COUNT(id) as total_calls,
            COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN id END) as success_calls,
            COUNT(CASE WHEN status_code >= 400 THEN id END) as error_calls,
            AVG(latency_ms) as avg_duration_ms,
            SUM(tokens_used) as total_tokens_used,
            SUM(cost_usd) as total_cost,
            MIN(created_at) as first_call_at,
            MAX(created_at) as last_call_at
        FROM llm_calls
        GROUP BY provider, model
    """))
    
    # API请求统计视图
    await conn.execute(text("""
        CREATE OR REPLACE VIEW api_stats AS
        SELECT 
            method,
            status_code,
            COUNT(id) as request_count,
            AVG(latency_ms) as avg_duration_ms,
            MIN(latency_ms) as min_duration_ms,
            MAX(latency_ms) as max_duration_ms,
            COUNT(CASE WHEN status_code >= 400 THEN id END) as error_count
        FROM api_logs
        GROUP BY method, status_code
    """))


async def create_optimization_indexes(conn):
    """创建优化索引"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_llm_calls_session_created ON llm_calls(session_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_timestamp ON performance_metrics(metric_name, timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_type_created ON error_logs(error_type, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_user_behaviors_session_created ON user_behaviors(session_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_intent_analyses_session_created ON intent_analyses(session_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_ad_recommendations_session_created ON ad_recommendations(session_id, created_at DESC)",
    ]
    
    for index_sql in indexes:
        await conn.execute(text(index_sql))


async def insert_default_config(engine):
    """插入默认配置"""
    async with engine.begin() as conn:
        default_configs = [
            ('app.name', '"Genesis AI App"', '应用名称'),
            ('app.version', '"1.0.0"', '应用版本'),
            ('app.debug', 'false', '调试模式'),
            ('llm.default_provider', '"openai"', '默认LLM提供商'),
            ('llm.openai.model', '"gpt-4"', 'OpenAI默认模型'),
            ('llm.qwen.model', '"qwen-max"', 'Qwen默认模型'),
            ('logging.level', '"INFO"', '日志级别'),
            ('logging.max_file_size', '10485760', '日志文件最大大小（字节）'),
            ('logging.backup_count', '5', '日志备份文件数量'),
        ]
        
        for key, value, description in default_configs:
            await conn.execute(text("""
                INSERT INTO system_config (key, value, description, is_active) 
                VALUES (:key, :value, :description, true)
                ON CONFLICT (key) DO UPDATE 
                SET value = EXCLUDED.value, description = EXCLUDED.description
            """), {"key": key, "value": value, "description": description})


async def verify_all_tables(engine):
    """验证所有表都存在"""
    expected_tables = {
        'users', 'user_sessions', 'chat_sessions', 'chat_messages',
        'user_behaviors', 'intent_analyses', 'ad_recommendations',
        'system_config', 'llm_calls', 'api_logs', 'tool_calls',
        'performance_metrics', 'error_logs', 'audit_logs'
    }
    
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        existing_tables = {row[0] for row in result.fetchall()}
        
        missing_tables = expected_tables - existing_tables
        if missing_tables:
            print(f"ERROR - 缺少表: {missing_tables}")
            return False
        
        extra_tables = existing_tables - expected_tables
        if extra_tables:
            print(f"WARNING - 额外表: {extra_tables}")
        
        print(f"OK - 所有必需表都存在 ({len(expected_tables)}/{len(existing_tables)})")
        return True


async def show_initialization_summary(engine):
    """显示初始化摘要"""
    async with engine.begin() as conn:
        # 统计表记录数
        tables_to_count = [
            'users', 'user_sessions', 'chat_sessions', 'chat_messages',
            'llm_calls', 'api_logs', 'tool_calls'
        ]
        
        print("\nINFO - 表记录统计:")
        for table in tables_to_count:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  - {table}: {count} 条记录")
        
        # 显示系统配置
        result = await conn.execute(text("""
            SELECT key, value, description 
            FROM system_config 
            WHERE is_active = true 
            ORDER BY key
        """))
        
        print("\nINFO - 系统配置:")
        for row in result.fetchall():
            key, value, description = row
            print(f"  - {key}: {value} ({description})")


if __name__ == "__main__":
    success = asyncio.run(initialize_complete_database())
    sys.exit(0 if success else 1)