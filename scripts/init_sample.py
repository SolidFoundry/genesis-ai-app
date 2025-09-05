# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def init_sample_data():
    """初始化示例数据"""
    try:
        from src.genesis.core.simple_container import container, init_resources, shutdown_resources
        from sqlalchemy import text
        
        print("正在初始化示例数据...")
        
        # 初始化容器
        await init_resources()
        
        # 获取数据库会话
        db_manager = container.core.db_manager()
        async with db_manager.session() as session:
            # 检查是否已有数据
            result = await session.execute(text("SELECT COUNT(*) FROM chat_sessions"))
            count = result.scalar()
            
            if count == 0:
                # 插入示例用户会话
                await session.execute(text("""
                    INSERT INTO chat_sessions (session_id, user_id, system_prompt) VALUES
                    ('session_001', 'user_001', '你是一个专业的AI助手，请帮助用户解决问题。'),
                    ('session_002', 'user_002', '你是一个代码助手，专门帮助用户解决编程问题。'),
                    ('session_003', 'user_003', '你是一个通用的AI助手，可以回答各种问题。')
                """))
                
                # 插入示例聊天消息
                await session.execute(text("""
                    INSERT INTO chat_messages (session_id, role, content) VALUES
                    ('session_001', 'user', '{"content": "你好，请介绍一下你自己"}'),
                    ('session_001', 'assistant', '{"content": "你好！我是一个AI助手，可以帮助你回答问题、提供信息、协助编程等。有什么我可以帮助你的吗？"}'),
                    ('session_002', 'user', '{"content": "如何用Python实现快速排序？"}'),
                    ('session_002', 'assistant', '{"content": "快速排序是一种高效的排序算法，以下是Python实现：\\n\\ndef quick_sort(arr):\\n    if len(arr) <= 1:\\n        return arr\\n    pivot = arr[len(arr) // 2]\\n    left = [x for x in arr if x < pivot]\\n    middle = [x for x in arr if x == pivot]\\n    right = [x for x in arr if x > pivot]\\n    return quick_sort(left) + middle + quick_sort(right)"}')
                """))
                
                # 插入示例用户行为
                await session.execute(text("""
                    INSERT INTO user_behaviors (session_id, user_id, behavior_type, behavior_data, detected_intent, intent_confidence) VALUES
                    ('session_001', 'user_001', 'view', '{"page": "/home", "duration": 30}', '页面浏览', 0.9),
                    ('session_001', 'user_001', 'search', '{"query": "AI助手", "results": 15}', '信息搜索', 0.8),
                    ('session_002', 'user_002', 'click', '{"element": "code_button", "page": "/programming"}', '编程学习', 0.95)
                """))
                
                # 插入示例意图分析
                await session.execute(text("""
                    INSERT INTO intent_analyses (session_id, user_id, primary_intent, secondary_intents, target_audience_segment, urgency_level, analysis_model, analysis_confidence) VALUES
                    ('session_001', 'user_001', '信息咨询', '["技术学习", "AI应用"]', '技术爱好者', 0.7, 'gpt-4', 0.85),
                    ('session_002', 'user_002', '编程学习', '["算法学习", "Python开发"]', '开发者', 0.9, 'gpt-4', 0.92)
                """))
                
                # 插入示例系统配置
                await session.execute(text("""
                    INSERT INTO system_config (key, value, description) VALUES
                    ('app.name', '"Genesis AI App"', '应用名称'),
                    ('app.version', '"1.0.0"', '应用版本'),
                    ('app.debug', 'false', '调试模式'),
                    ('llm.default_provider', '"openai"', '默认LLM提供商'),
                    ('database.pool_size', '20', '数据库连接池大小'),
                    ('api.rate_limit', '100', 'API速率限制')
                """))
                
                await session.commit()
                print("示例数据初始化成功")
                return True
            else:
                print("数据库中已有数据，跳过示例数据初始化")
                return True
                
    except Exception as e:
        print(f"示例数据初始化失败: {e}")
        return False
    finally:
        try:
            await shutdown_resources()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(init_sample_data())
    sys.exit(0 if success else 1)