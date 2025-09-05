"""
MCP基础工具模块
============

本模块提供基础的MCP工具实现。
"""

from fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("Genesis AI App MCP Server")


@mcp.tool()
def greet(name: str) -> str:
    """
    向用户问好
    
    Args:
        name: 用户名称
        
    Returns:
        问好消息
    """
    return f"Hello, {name}!"


@mcp.tool()
def echo(message: str) -> str:
    """
    回显消息
    
    Args:
        message: 要回显的消息
        
    Returns:
        原始消息
    """
    return message


@mcp.tool()
def get_server_info() -> dict:
    """
    获取服务器信息
    
    Returns:
        服务器信息字典
    """
    return {
        "name": "Genesis MCP Server",
        "version": "1.0.0",
        "status": "running",
        "tools": ["greet", "echo", "get_server_info"]
    }


def register_basic_tools(mcp_instance: FastMCP) -> None:
    """注册基础工具到指定的MCP实例"""
    # 这个函数保持向后兼容，但现在主要使用直接装饰器方式
    pass