"""
Genesis AI 应用调试路由器
=======================

本模块提供调试和测试端点，用于验证数据库会话和LLM服务的集成。
这些端点主要用于开发环境下的功能验证。

注意：以下划线开头的路由器表示临时或内部使用，不建议在生产环境中使用。
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from dependency_injector.wiring import Provide, inject

from src.genesis.core.simple_container_fixed import container
# from src.genesis.infrastructure.llm.interface import LLMProviderInterface
# from src.genesis.infrastructure.database import get_db_session


router = APIRouter(
    prefix="/_debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)


@router.get("/db-status")
async def db_status(session: AsyncSession = Depends(get_db_session)):
    """
    数据库连接状态检查端点
    
    执行简单的SQL查询来验证数据库连接是否正常工作。
    
    Returns:
        dict: 包含数据库连接状态和查询结果的字典
    """
    try:
        # 执行简单的查询来测试连接
        result = await session.execute(text("SELECT 1 as test_value"))
        test_value = result.scalar_one_or_none()
        
        # 获取连接池状态
        db_manager = container.core.db_manager()
        pool_status = db_manager.get_pool_status()
        
        return {
            "status": "healthy",
            "message": "数据库连接正常",
            "test_query_result": test_value,
            "pool_info": pool_status,
            "timestamp": "2025-09-03T00:00:00Z"  # 实际应用中应该使用datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "message": "数据库连接失败",
                "error": str(e),
                "timestamp": "2025-09-03T00:00:00Z"
            }
        )


class LLMEchoRequest(BaseModel):
    """LLM回显请求模型"""
    message: str = Field(..., description="要发送给LLM的消息", min_length=1, max_length=1000)
    temperature: float = Field(0.7, description="温度参数，控制输出的随机性", ge=0.0, le=2.0)
    max_tokens: int = Field(500, description="最大令牌数", ge=1, le=2000)


@router.post("/llm-echo")
@inject
async def llm_echo(
    request: LLMEchoRequest,
    llm_provider: LLMProviderInterface = Depends(Provide[container.infrastructure.llm_provider])
):
    """
    LLM回显端点
    
    将用户消息发送给当前配置的LLM提供商并返回响应。
    用于验证LLM服务的集成和配置是否正确。
    
    Args:
        request: 包含用户消息和LLM参数的请求对象
        llm_provider: 通过依赖注入的LLM提供商实例
        
    Returns:
        dict: 包含LLM响应的字典
    """
    try:
        # 构建消息格式
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        # 调用LLM提供商
        response = await llm_provider.chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 提取响应内容
        choices = response.get("choices", [])
        if not choices:
            raise HTTPException(
                status_code=500,
                detail="LLM返回了空响应"
            )
        
        message = choices[0].get("message", {})
        content = message.get("content", "")
        
        # 获取提供商信息
        provider_name = llm_provider.get_provider_name()
        default_model = llm_provider.get_default_model()
        
        return {
            "status": "success",
            "provider": {
                "name": provider_name,
                "model": default_model
            },
            "request": {
                "message": request.message,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            },
            "response": {
                "content": content,
                "raw_response": response
            },
            "timestamp": "2025-09-03T00:00:00Z"  # 实际应用中应该使用datetime.utcnow()
        }
        
    except Exception as e:
        # 检查是否是LLM提供商特定的异常
        error_message = str(e)
        status_code = 500
        
        if "authentication" in error_message.lower() or "api_key" in error_message.lower():
            status_code = 401
        elif "rate_limit" in error_message.lower() or "429" in error_message:
            status_code = 429
        elif "timeout" in error_message.lower():
            status_code = 504
        
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": "error",
                "message": "LLM请求失败",
                "error": error_message,
                "timestamp": "2025-09-03T00:00:00Z"
            }
        )


@router.get("/system-info")
async def system_info():
    """
    系统信息端点
    
    返回应用的基本配置和状态信息，用于调试和验证。
    """
    try:
        # 获取当前配置
        settings = container.core.config()
        
        # 获取数据库管理器状态
        db_manager = container.core.db_manager()
        db_healthy = await db_manager.health_check()
        
        # 获取LLM提供商信息
        llm_provider = container.infrastructure.llm_provider()
        llm_healthy = await llm_provider.health_check()
        
        return {
            "application": {
                "name": settings.app.name,
                "version": settings.app.version,
                "environment": settings.env,
                "debug": settings.app.debug
            },
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "url": settings.database.url,
                "pool_size": settings.database.pool_size
            },
            "llm": {
                "status": "healthy" if llm_healthy else "unhealthy",
                "default_provider": settings.llm.default_provider,
                "current_provider": llm_provider.get_provider_name(),
                "current_model": llm_provider.get_default_model()
            },
            "features": [
                "Database connection pool",
                "LLM provider abstraction",
                "Dependency injection",
                "Async SQLAlchemy",
                "FastAPI integration"
            ],
            "timestamp": "2025-09-03T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "获取系统信息失败",
                "error": str(e),
                "timestamp": "2025-09-03T00:00:00Z"
            }
        )


# 导出路由器
__all__ = ["router"]