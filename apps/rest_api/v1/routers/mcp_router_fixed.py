"""
Genesis AI 应用 MCP 路由器 - 修复版本
======================================

本模块提供 MCP (Model Context Protocol) 相关的 API 端点，使用FastMCP官方客户端。
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import logging
import json
import asyncio

from src.genesis.core.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["MCP"])


class MCPToolCallRequest(BaseModel):
    """MCP 工具调用请求模型"""
    tool_name: str = Field("greet", description="工具名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "greet",
                "arguments": {"name": "Alice"}
            }
        }


class MCPToolCallResponse(BaseModel):
    """MCP 工具调用响应模型"""
    success: bool = Field(True, description="调用是否成功")
    result: Optional[Dict[str, Any]] = Field(None, description="调用结果")
    error: Optional[str] = Field(None, description="错误信息")
    tool_name: str = Field(description="工具名称")


class MCPStatusResponse(BaseModel):
    """MCP 服务器状态响应模型"""
    server_running: bool = Field(False, description="服务器是否运行")
    server_url: str = Field(description="服务器URL")
    available_tools: list = Field(default_factory=list, description="可用工具列表")
    error: Optional[str] = Field(None, description="错误信息")


class MCPClient:
    """MCP 客户端封装类 - 使用FastMCP官方客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.mcp_url = f"{server_url}/mcp"
        self.client = None
    
    async def _get_client(self):
        """获取FastMCP客户端实例"""
        if self.client is None:
            from fastmcp import Client
            self.client = Client(self.mcp_url)
        return self.client
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用 MCP 工具"""
        try:
            client = await self._get_client()
            
            # 在客户端上下文中调用工具
            async with client:
                result = await client.call_tool(tool_name, arguments or {})
                
                # 转换结果格式
                return {
                    "success": True,
                    "result": {
                        "content": [{"type": item.type, "text": item.text} for item in result.content],
                        "structured_content": result.structured_content,
                        "data": result.data,
                        "is_error": result.is_error
                    },
                    "tool_name": tool_name
                }
                
        except Exception as e:
            logger.error(f"MCP 工具调用异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        try:
            client = await self._get_client()
            
            # 在客户端上下文中获取工具列表
            async with client:
                tools = await client.list_tools()
                
                # 转换工具格式
                formatted_tools = []
                for tool in tools:
                    formatted_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                        "outputSchema": tool.outputSchema
                    })
                
                return {
                    "success": True,
                    "result": {"tools": formatted_tools},
                    "available_tools": formatted_tools
                }
                
        except Exception as e:
            logger.error(f"获取 MCP 工具列表异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "available_tools": []
            }


# 创建 MCP 客户端实例
# 处理配置可能是字典或对象的情况
mcp_server_config = settings.server.mcp_server
if isinstance(mcp_server_config, dict):
    mcp_port = mcp_server_config.get('port', 8888)
else:
    mcp_port = mcp_server_config.port

mcp_client = MCPClient(
    server_url=f"http://127.0.0.1:{mcp_port}"
)


@router.post("/tools/call", response_model=MCPToolCallResponse)
async def call_mcp_tool(request: MCPToolCallRequest):
    """
    调用 MCP 工具
    
    使用FastMCP官方客户端连接和调用MCP服务器上的工具。
    """
    try:
        logger.info(f"调用 MCP 工具: {request.tool_name}, 参数: {request.arguments}")
        
        # 调用 MCP 工具
        result = await mcp_client.call_tool(request.tool_name, request.arguments)
        
        logger.info(f"MCP 工具调用结果: {result}")
        
        return MCPToolCallResponse(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error"),
            tool_name=request.tool_name
        )
        
    except Exception as e:
        logger.error(f"调用 MCP 工具时发生异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"调用 MCP 工具失败: {str(e)}"
        )


@router.get("/tools/list", response_model=MCPStatusResponse)
async def list_mcp_tools():
    """获取 MCP 服务器可用工具列表"""
    try:
        logger.info("获取 MCP 工具列表")
        
        # 获取工具列表
        result = await mcp_client.list_tools()
        
        logger.info(f"MCP 工具列表结果: {result}")
        
        return MCPStatusResponse(
            server_running=result.get("success", False),
            server_url=mcp_client.server_url,
            available_tools=result.get("available_tools", []),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"获取 MCP 工具列表时发生异常: {e}")
        return MCPStatusResponse(
            server_running=False,
            server_url=mcp_client.server_url,
            available_tools=[],
            error=str(e)
        )


@router.get("/status", response_model=MCPStatusResponse)
async def get_mcp_status():
    """检查 MCP 服务器状态"""
    try:
        logger.info("检查 MCP 服务器状态")
        
        # 尝试获取工具列表来验证服务器是否运行
        result = await mcp_client.list_tools()
        
        return MCPStatusResponse(
            server_running=result.get("success", False),
            server_url=mcp_client.server_url,
            available_tools=result.get("available_tools", []),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"检查 MCP 服务器状态时发生异常: {e}")
        return MCPStatusResponse(
            server_running=False,
            server_url=mcp_client.server_url,
            available_tools=[],
            error=str(e)
        )


@router.post("/demo/greet")
async def demo_greet_user(name: str = "World"):
    """
    演示：使用 MCP greet 工具问候用户
    
    这是一个简化的演示端点，展示如何调用 MCP 服务器上的 greet 工具。
    """
    try:
        logger.info(f"演示 greet 工具，用户名: {name}")
        
        # 调用 MCP greet 工具
        result = await mcp_client.call_tool("greet", {"name": name})
        
        if result.get("success"):
            return {
                "message": "演示成功",
                "tool_result": result.get("result"),
                "tool_name": "greet"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"MCP 工具调用失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"演示 greet 工具时发生异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"演示失败: {str(e)}"
        )


@router.post("/demo/echo")
async def demo_echo_message(message: str = "Hello from MCP!"):
    """
    演示：使用 MCP echo 工具回显消息
    
    这是一个简化的演示端点，展示如何调用 MCP 服务器上的 echo 工具。
    """
    try:
        logger.info(f"演示 echo 工具，消息: {message}")
        
        # 调用 MCP echo 工具
        result = await mcp_client.call_tool("echo", {"message": message})
        
        if result.get("success"):
            return {
                "message": "演示成功",
                "tool_result": result.get("result"),
                "tool_name": "echo"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"MCP 工具调用失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"演示 echo 工具时发生异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"演示失败: {str(e)}"
        )


@router.get("/demo/server-info")
async def demo_server_info():
    """
    演示：使用 MCP get_server_info 工具获取服务器信息
    
    这是一个简化的演示端点，展示如何调用 MCP 服务器上的 get_server_info 工具。
    """
    try:
        logger.info("演示 get_server_info 工具")
        
        # 调用 MCP get_server_info 工具
        result = await mcp_client.call_tool("get_server_info", {})
        
        if result.get("success"):
            return {
                "message": "演示成功",
                "tool_result": result.get("result"),
                "tool_name": "get_server_info"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"MCP 工具调用失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"演示 get_server_info 工具时发生异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"演示失败: {str(e)}"
        )


# 示例：如何在其他服务中使用 MCP 客户端
async def example_mcp_usage():
    """
    示例：如何在其他服务中使用 MCP 客户端
    
    这个函数展示了如何在应用的其他部分使用 MCP 客户端。
    """
    try:
        # 调用 greet 工具
        greet_result = await mcp_client.call_tool("greet", {"name": "Alice"})
        logger.info(f"Greet 结果: {greet_result}")
        
        # 调用 echo 工具
        echo_result = await mcp_client.call_tool("echo", {"message": "Hello World"})
        logger.info(f"Echo 结果: {echo_result}")
        
        # 获取服务器信息
        server_info = await mcp_client.call_tool("get_server_info", {})
        logger.info(f"服务器信息: {server_info}")
        
        return {
            "greet": greet_result,
            "echo": echo_result,
            "server_info": server_info
        }
        
    except Exception as e:
        logger.error(f"MCP 使用示例失败: {e}")
        return None