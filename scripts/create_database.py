# -*- coding: utf-8 -*-
"""
创建genesis数据库脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def create_database():
    """创建genesis数据库"""
    try:
        import asyncpg
        
        # 连接到PostgreSQL默认数据库
        connection = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="heimdall",
            password="heimdall_password",
            database="postgres"  # 连接到默认数据库
        )
        
        print("成功连接到PostgreSQL服务器")
        
        # 检查数据库是否已存在
        exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'genesis_db'"
        )
        
        if exists:
            print("数据库 'genesis_db' 已存在，跳过创建")
        else:
            # 创建数据库
            await connection.execute('CREATE DATABASE "genesis_db"')
            print("成功创建数据库 'genesis_db'")
        
        await connection.close()
        return True
        
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

async def main():
    """主函数"""
    print("=== 创建Genesis数据库 ===")
    
    if await create_database():
        print("数据库创建完成")
        return True
    else:
        print("数据库创建失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)