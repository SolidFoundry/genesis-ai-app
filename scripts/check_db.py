# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def check_database():
    """检查数据库连接"""
    try:
        from src.genesis.core.simple_container import container, init_resources, shutdown_resources
        
        print("正在检查数据库连接...")
        
        # 初始化容器
        await init_resources()
        
        # 获取数据库管理器
        db_manager = container.core.db_manager()
        
        # 健康检查
        is_healthy = await db_manager.health_check()
        if is_healthy:
            print("数据库连接正常")
            return True
        else:
            print("数据库连接异常")
            return False
            
    except Exception as e:
        print(f"数据库连接检查失败: {e}")
        return False
    finally:
        try:
            await shutdown_resources()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)