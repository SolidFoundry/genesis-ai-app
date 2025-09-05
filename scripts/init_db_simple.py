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
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy import text
        
        # 创建基础类
        class Base(DeclarativeBase):
            pass
        
        # 创建数据库引擎
        engine = create_async_engine(
            "postgresql+asyncpg://genesis:genesis_password@localhost:5432/genesis_db",
            echo=False
        )
        
        print("正在初始化数据库...")
        
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
                # 创建所有表（如果有的话）
                print("数据库表不存在，但暂时跳过表创建")
                print("数据库连接测试成功")
                return True
            else:
                print("数据库表已存在，连接正常")
                return True
                
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    finally:
        try:
            if 'engine' in locals():
                await engine.dispose()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)