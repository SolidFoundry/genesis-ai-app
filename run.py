"""
Genesis AI 应用启动脚本
=======================

这是应用的启动入口，提供灵活的启动方式。
支持直接运行和命令行参数配置。

使用方式：
    python run.py                    # 使用默认配置启动
    python run.py --host 0.0.0.0     # 指定主机
    python run.py --port 8000        # 指定端口
    python run.py --reload           # 开启热重载
    python run.py --init-db          # 初始化数据库
    python run.py --init-sample      # 初始化示例数据
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

import uvicorn

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault("APP_ENV", "development")


def parse_args():
    """解析命令行参数"""
    
    parser = argparse.ArgumentParser(
        description="Genesis AI 应用启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  %(prog)s                          # 使用默认配置启动
  %(prog)s --host 0.0.0.0           # 指定主机
  %(prog)s --port 8000              # 指定端口
  %(prog)s --reload                 # 开启热重载
  %(prog)s --init-db                # 初始化数据库
  %(prog)s --init-sample            # 初始化示例数据
        """
    )
    
    # 服务器配置
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器监听地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器监听端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开启热重载模式"
    )
    
    # 环境配置
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "production"],
        default="development",
        help="运行环境 (默认: development)"
    )
    
    # 数据库初始化选项
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="初始化数据库结构"
    )
    
    parser.add_argument(
        "--init-sample",
        action="store_true",
        help="初始化示例数据"
    )
    
    # 自动初始化选项
    parser.add_argument(
        "--auto-init",
        action="store_true",
        help="自动初始化所有必需的组件"
    )
    
    return parser.parse_args()


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print(f"{description}成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"{description}失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"{description}异常: {e}")
        return False


def check_poetry():
    """检查Poetry是否安装"""
    try:
        result = subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Poetry 已安装: {result.stdout.strip()}")
            return True
        else:
            print("Poetry 未安装或无法运行")
            return False
    except Exception:
        print("Poetry 未安装")
        return False


def install_dependencies():
    """安装项目依赖"""
    return run_command("poetry install", "安装项目依赖")


def initialize_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    try:
        # 使用修复后的数据库初始化脚本
        init_script = project_root / "scripts" / "init_db_fixed.py"
        
        # 运行初始化脚本
        result = subprocess.run([
            sys.executable, str(init_script)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("数据库初始化成功")
            print(result.stdout)
            return True
        else:
            print("数据库初始化失败")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"数据库初始化异常: {e}")
        return False


def initialize_sample_data():
    """初始化示例数据"""
    print("正在初始化示例数据...")
    
    try:
        # 使用修复后的示例数据初始化脚本
        sample_script = project_root / "scripts" / "init_sample_fixed.py"
        if not sample_script.exists():
            print("错误: 找不到示例数据初始化脚本")
            return False
        
        # 运行示例数据初始化脚本
        result = subprocess.run([
            sys.executable, str(sample_script)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("示例数据初始化成功")
            print(result.stdout)
            return True
        else:
            print("示例数据初始化失败")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"示例数据初始化异常: {e}")
        return False


def check_database_connection():
    """检查数据库连接"""
    print("正在检查数据库连接...")
    
    try:
        # 使用修复后的数据库检查脚本
        check_script = project_root / "scripts" / "check_db_fixed.py"
        
        # 运行数据库检查脚本
        result = subprocess.run([
            sys.executable, str(check_script)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("数据库连接正常")
            print(result.stdout)
            return True
        else:
            print("数据库连接失败")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"数据库连接检查异常: {e}")
        return False


def main():
    """主函数"""
    
    # 解析命令行参数
    args = parse_args()
    
    # 设置环境变量
    os.environ["APP_ENV"] = args.env
    
    print("=== Genesis AI 应用启动器 ===")
    print(f"运行环境: {args.env}")
    print(f"服务地址: http://{args.host}:{args.port}")
    print("=" * 50)
    
    # 1. 检查Poetry
    if not check_poetry():
        print("请先安装 Poetry: https://python-poetry.org/docs/#installation")
        print("或者运行: pip install poetry")
        return
    
    # 2. 检查虚拟环境
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("虚拟环境不存在，正在创建...")
        if not install_dependencies():
            print("依赖安装失败，请检查网络连接或手动安装")
            return
    else:
        print("虚拟环境已存在")
    
    # 3. 自动初始化（如果需要）
    if args.auto_init:
        print("正在执行自动初始化...")
        
        # 初始化数据库
        if not initialize_database():
            print("数据库初始化失败，请检查数据库配置")
            return
        
        # 初始化示例数据
        if not initialize_sample_data():
            print("示例数据初始化失败")
            return
    
    # 4. 手动初始化（如果需要）
    if args.init_db:
        if not initialize_database():
            print("数据库初始化失败，请检查数据库配置")
            return
    
    if args.init_sample:
        if not initialize_sample_data():
            print("示例数据初始化失败")
            return
    
    # 5. 检查数据库连接
    if not check_database_connection():
        print("数据库连接失败，请检查数据库配置和连接")
        print("提示: 可以使用 --init-db 参数初始化数据库")
        print("或者使用 --auto-init 参数自动初始化所有组件")
        return
    
    print("=" * 50)
    print("启动应用...")
    print(f"API 文档: http://{args.host}:{args.port}/docs")
    print(f"健康检查: http://{args.host}:{args.port}/health")
    print(f"调试端点: http://{args.host}:{args.port}/v1/_debug/system-info")
    print("=" * 50)
    
    try:
        # 启动服务器
        uvicorn.run(
            "apps.rest_api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭服务...")
        
    except Exception as e:
        print(f"\n启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()