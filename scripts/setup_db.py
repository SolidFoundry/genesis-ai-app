# -*- coding: utf-8 -*-
"""
Genesis AI 应用数据库设置脚本
=========================

本脚本帮助用户快速设置 PostgreSQL 数据库环境。
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{description}...")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✓ {description}成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"✗ {description}失败")
            if result.stderr:
                print(f"错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {description}超时")
        return False
    except Exception as e:
        print(f"✗ {description}异常: {e}")
        return False

def check_docker():
    """检查 Docker 是否安装"""
    print("检查 Docker 环境...")
    
    if not run_command("docker --version", "检查 Docker 版本"):
        print("请先安装 Docker Desktop")
        return False
    
    if not run_command("docker-compose --version", "检查 Docker Compose"):
        print("请确保 Docker Compose 已安装")
        return False
    
    print("✓ Docker 环境正常")
    return True

def setup_postgres_container():
    """设置 PostgreSQL 容器"""
    print("\n设置 PostgreSQL 数据库容器...")
    
    # 检查容器是否已经存在
    result = subprocess.run(
        "docker ps -a --filter 'name=genesis-postgres' --format '{{.Names}}'",
        shell=True, capture_output=True, text=True
    )
    
    if "genesis-postgres" in result.stdout:
        print("发现现有的 genesis-postgres 容器")
        
        # 检查容器是否正在运行
        result = subprocess.run(
            "docker ps --filter 'name=genesis-postgres' --format '{{.Status}}'",
            shell=True, capture_output=True, text=True
        )
        
        if "Up" in result.stdout:
            print("✓ PostgreSQL 容器已在运行")
            return True
        else:
            print("启动现有的 PostgreSQL 容器...")
            if run_command("docker start genesis-postgres", "启动容器"):
                print("等待数据库启动...")
                time.sleep(5)
                return True
            else:
                print("启动容器失败，尝试重新创建")
                run_command("docker rm -f genesis-postgres", "删除现有容器")
    
    # 创建新容器
    print("创建新的 PostgreSQL 容器...")
    command = (
        "docker run --name genesis-postgres "
        "-e POSTGRES_USER=genesis "
        "-e POSTGRES_PASSWORD=genesis_password "
        "-e POSTGRES_DB=genesis_db "
        "-p 5432:5432 "
        "-d postgres:15"
    )
    
    if run_command(command, "创建 PostgreSQL 容器"):
        print("等待数据库启动...")
        time.sleep(10)
        return True
    else:
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    # 使用简单的 Python 脚本测试连接
    test_script = '''
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    try:
        engine = create_async_engine("postgresql+asyncpg://genesis:genesis_password@localhost:5432/genesis_db", echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
            await engine.dispose()
            return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
'''
    
    # 写入临时文件
    temp_script = Path("temp_test_db.py")
    temp_script.write_text(test_script)
    
    try:
        result = subprocess.run([
            sys.executable, str(temp_script)
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ 数据库连接测试通过")
            print(result.stdout)
            return True
        else:
            print("✗ 数据库连接测试失败")
            if result.stderr:
                print(result.stderr)
            return False
    finally:
        if temp_script.exists():
            temp_script.unlink()

def main():
    """主函数"""
    print("=== Genesis AI 应用数据库设置 ===")
    print("本脚本将帮助您设置 PostgreSQL 数据库环境")
    print("=" * 50)
    
    # 1. 检查 Docker
    if not check_docker():
        print("\n请先安装 Docker Desktop 再继续")
        return False
    
    # 2. 设置 PostgreSQL
    if not setup_postgres_container():
        print("\nPostgreSQL 容器设置失败")
        return False
    
    # 3. 测试连接
    if not test_database_connection():
        print("\n数据库连接测试失败")
        print("请检查 Docker Desktop 是否正在运行")
        print("并确保端口 5432 没有被其他程序占用")
        return False
    
    print("\n" + "=" * 50)
    print("✓ 数据库设置完成!")
    print("现在您可以运行以下命令启动应用:")
    print("  python run.py --auto-init")
    print("  或")
    print("  start.bat")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)