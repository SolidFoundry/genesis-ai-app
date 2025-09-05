# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def init_database():
    """初始化数据库"""
    try:
        from src.genesis.infrastructure.database.models import Base
        from src.genesis.core.simple_container import container, init_resources, shutdown_resources
        from sqlalchemy import text
        
        print("正在初始化数据库...")
        
        # 初始化容器
        await init_resources()
        
        # 创建表结构
        db_manager = container.core.db_manager()
        engine = db_manager.engine
        
        async with engine.begin() as conn:
            # 检查是否已经初始化
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'users'
                )
            """))
            tables_exist = result.scalar()
            
            if not tables_exist:
                # 创建所有表
                await conn.run_sync(Base.metadata.create_all)
                print("数据库表结构创建成功")
                
                # 插入默认配置
                await conn.execute(text("""
                    INSERT INTO system_config (key, value, description) VALUES
                    ('app.name', '"Genesis AI App"', '应用名称'),
                    ('app.version', '"1.0.0"', '应用版本'),
                    ('app.debug', 'false', '调试模式'),
                    ('llm.default_provider', '"openai"', '默认LLM提供商')
                    ON CONFLICT (key) DO NOTHING
                """))
                print("默认配置插入成功")
                
                return True
            else:
                print("数据库表已存在，跳过初始化")
                return True
                
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    finally:
        try:
            await shutdown_resources()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)