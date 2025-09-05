# -*- coding: utf-8 -*-
"""
为Genesis项目创建独立的数据库用户
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def create_genesis_user():
    """创建Genesis数据库用户"""
    try:
        import asyncpg
        
        # 连接到PostgreSQL默认数据库（使用现有用户）
        connection = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="heimdall",
            password="heimdall_password",
            database="postgres"
        )
        
        print("成功连接到PostgreSQL服务器")
        
        # 检查用户是否已存在
        user_exists = await connection.fetchval(
            "SELECT 1 FROM pg_roles WHERE rolname = 'genesis'"
        )
        
        if user_exists:
            print("用户 'genesis' 已存在，跳过创建")
        else:
            # 创建新用户
            await connection.execute('''
                CREATE USER genesis WITH 
                PASSWORD 'genesis_password' 
                NOSUPERUSER 
                NOCREATEDB 
                NOCREATEROLE 
                INHERIT 
                LOGIN
            ''')
            print("成功创建用户 'genesis'")
        
        # 为新用户授予genesis_db的所有权限
        await connection.execute('''
            GRANT ALL PRIVILEGES ON DATABASE genesis_db TO genesis
        ''')
        print("成功授予genesis_db数据库权限给用户genesis")
        
        # 连接到genesis_db数据库并授予schema权限
        await connection.close()
        genesis_connection = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="heimdall",
            password="heimdall_password",
            database="genesis_db"
        )
        
        # 授予schema权限
        await genesis_connection.execute('''
            GRANT ALL ON SCHEMA public TO genesis
        ''')
        print("成功授予public schema权限")
        
        # 设置默认权限
        await genesis_connection.execute('''
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO genesis
        ''')
        await genesis_connection.execute('''
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO genesis
        ''')
        print("成功设置默认权限")
        
        await genesis_connection.close()
        return True
        
    except Exception as e:
        print(f"创建用户失败: {e}")
        return False

async def main():
    """主函数"""
    print("=== 创建Genesis数据库用户 ===")
    
    if await create_genesis_user():
        print("Genesis用户创建完成")
        return True
    else:
        print("Genesis用户创建失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)