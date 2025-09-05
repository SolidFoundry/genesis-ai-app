"""
Genesis AI 应用简化调试路由器
=========================

提供基本的调试端点
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.genesis.ai_tools.registry import tool_registry


router = APIRouter(
    prefix="/_debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)


@router.get("/db-status")
async def db_status(request: Request):
    """
    数据库连接状态检查端点
    
    执行简单的SQL查询来验证数据库连接是否正常工作。
    
    Returns:
        dict: 包含数据库连接状态和查询结果的字典
    """
    try:
        # 获取数据库管理器
        db_manager = request.app.state.db_manager
        
        # 检查连接状态
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            # 获取连接池状态
            pool_status = db_manager.get_pool_status()
            
            return {
                "status": "healthy",
                "message": "数据库连接正常",
                "pool_info": pool_status,
            }
        else:
            return {
                "status": "unhealthy",
                "message": "数据库连接异常",
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据库状态检查失败: {str(e)}"
        )


@router.get("/system-info")
async def system_info(request: Request) -> Dict[str, Any]:
    """
    系统信息端点
    
    返回应用的基本信息和配置状态。
    
    Returns:
        dict: 包含系统信息的字典
    """
    try:
        # 获取数据库管理器
        db_manager = request.app.state.db_manager
        
        # 获取连接池状态
        pool_status = db_manager.get_pool_status()
        
        return {
            "app": {
                "name": "Genesis AI App",
                "version": "1.0.0",
                "status": "running"
            },
            "database": {
                "status": "connected",
                "pool_info": pool_status
            },
            "features": [
                "FastAPI REST API",
                "SQLAlchemy ORM",
                "Async Database Connection",
                "Dependency Injection"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取系统信息失败: {str(e)}"
        )


@router.get("/tools")
async def get_registered_tools(request: Request):
    """
    获取已注册的AI工具列表
    
    返回当前系统中所有已注册的AI工具信息，
    包括工具名称、描述和参数定义。
    
    Returns:
        dict: 包含工具列表和详细信息的字典
    """
    try:
        # 获取所有已注册的工具schemas
        tool_schemas = tool_registry.get_all_schemas()
        
        # 提取工具信息
        tools_info = []
        for tool_schema in tool_schemas:
            tool_info = {
                "name": tool_schema["function"]["name"],
                "description": tool_schema["function"]["description"],
                "parameters": tool_schema["function"]["parameters"]
            }
            tools_info.append(tool_info)
        
        return {
            "count": len(tools_info),
            "tools": tools_info,
            "raw_schemas": tool_schemas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取工具信息失败: {str(e)}"
        )