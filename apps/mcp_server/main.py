"""
MCP服务主入口模块
==============

本模块是MCP服务的入口点，负责初始化和启动服务。
"""

import os
import sys
import logging
from pathlib import Path

from apps.mcp_server.v1.tools.basic import mcp
from apps.mcp_server.config import mcp_config

def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "mcp_server.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("正在启动 Genesis MCP 服务器...")
    
    try:
        # 获取端口配置，支持环境变量覆盖
        port = int(os.environ.get('MCP_PORT', 8888))  # 默认使用8888端口
        host = os.environ.get('MCP_HOST', '127.0.0.1')
        
        logger.info(f"服务配置 - 主机: {host}, 端口: {port}")
        
        # 启动MCP服务器
        logger.info("正在启动 FastMCP 服务器...")
        logger.info("服务器正在初始化，请稍候...")
        
        # 增加初始化延迟，确保服务器完全启动
        import time
        time.sleep(2)  # 等待2秒确保初始化完成
        
        mcp.run(transport="http", host=host, port=port)
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"启动MCP服务器失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()