# -*- coding: utf-8 -*-
"""
修复的示例数据初始化脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def init_sample_data():
    """初始化示例数据"""
    try:
        from src.genesis.infrastructure.database.manager import DatabaseManager
        from src.genesis.core.settings import settings
        from sqlalchemy import text
        
        print("正在初始化示例数据...")
        
        # 创建数据库管理器
        db_manager = DatabaseManager(settings.database)
        
        # 初始化连接
        await db_manager.initialize()
        
        # 获取数据库会话
        async with db_manager.session() as session:
            # 检查是否已有数据
            result = await session.execute(text("SELECT COUNT(*) FROM chat_sessions"))
            count = result.scalar()
            
            if count == 0:
                # 插入示例会话（使用 ON CONFLICT DO NOTHING 避免重复）
                await session.execute(text("""
                    INSERT INTO chat_sessions (session_id, system_prompt) VALUES
                    ('session_001', '你是一个专业的AI助手，请帮助用户解决问题。'),
                    ('session_002', '你是一个代码助手，专门帮助用户解决编程问题。'),
                    ('session_003', '你是一个通用的AI助手，可以回答各种问题。')
                    ON CONFLICT (session_id) DO NOTHING
                """))
                
                # 插入示例消息
                await session.execute(text("""
                    INSERT INTO chat_messages (session_id, role, content) VALUES
                    ('session_001', 'user', '{"content": "你好，请介绍一下你自己"}'),
                    ('session_001', 'assistant', '{"content": "你好！我是一个AI助手，可以帮助你回答问题、提供信息、协助编程等。有什么我可以帮助你的吗？"}')
                """))
                
                # 插入示例用户会话（使用 ON CONFLICT DO NOTHING 避免重复）
                await session.execute(text("""
                    INSERT INTO user_sessions (session_id, user_id, user_segment, preferences) VALUES
                    ('user_session_001', 'user_001', 'developer', '{"preferred_language": "python", "experience_level": "intermediate"}'),
                    ('user_session_002', 'user_002', 'designer', '{"preferred_tools": ["figma", "adobe"], "project_type": "web_design"}')
                    ON CONFLICT (session_id) DO NOTHING
                """))
                
                # 插入示例用户行为
                await session.execute(text("""
                    INSERT INTO user_behaviors (session_id, user_id, behavior_type, behavior_data) VALUES
                    ('user_session_001', 'user_001', 'page_view', '{"page": "/home", "duration": 5.2}'),
                    ('user_session_001', 'user_001', 'search', '{"query": "python tutorial", "results_count": 10}')
                """))
                
                await session.commit()
                print("示例数据初始化成功")
                return True
            else:
                print("数据库中已有数据，跳过示例数据初始化")
                return True
                
    except Exception as e:
        print(f"示例数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            await db_manager.close()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(init_sample_data())
    sys.exit(0 if success else 1)