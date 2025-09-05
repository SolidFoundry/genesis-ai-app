"""
MCP工具路由模块
============

本模块负责管理和注册所有MCP工具。
"""

from fastmcp import FastMCP

from apps.mcp_server.v1.tools.basic import register_basic_tools


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self, mcp: FastMCP):
        """初始化工具注册表"""
        self.mcp = mcp
    
    def register_all_tools(self) -> None:
        """注册所有工具"""
        # 注册基础工具
        register_basic_tools(self.mcp)
        
        # TODO: 未来可以在这里添加更多工具类别
        # from apps.mcp_server.v1.tools.database import register_database_tools
        # register_database_tools(self.mcp)
        
        # from apps.mcp_server.v1.tools.llm import register_llm_tools
        # register_llm_tools(self.mcp)


def create_tool_registry(mcp: FastMCP) -> ToolRegistry:
    """创建工具注册表实例"""
    return ToolRegistry(mcp)