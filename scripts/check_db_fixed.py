# -*- coding: utf-8 -*-
"""
修复的数据库连接检查脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def check_database():
    """检查数据库连接"""
    try:
        from src.genesis.infrastructure.database.manager import DatabaseManager
        from src.genesis.core.settings import settings
        
        print("正在检查数据库连接...")
        
        # 创建数据库管理器
        db_manager = DatabaseManager(settings.database)
        
        # 初始化连接
        await db_manager.initialize()
        
        # 健康检查
        is_healthy = await db_manager.health_check()
        if is_healthy:
            print("数据库连接正常")
            await db_manager.close()
            return True
        else:
            print("数据库连接异常")
            await db_manager.close()
            return False
            
    except Exception as e:
        print(f"数据库连接检查失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)