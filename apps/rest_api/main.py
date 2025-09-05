"""
Genesis AI 应用 REST API 主入口
================================

这是 FastAPI 应用程序的入口点，负责创建和配置 FastAPI 应用实例。
集成了企业级的日志系统、中间件和监控功能。

主要功能：
- 创建 FastAPI 应用实例
- 配置基本路由
- 集成健康检查端点
- 提供自动 API 文档
- 企业级日志系统
- 请求追踪和性能监控
"""

import logging
import logging.config
import yaml
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from datetime import datetime

# from src.genesis.core.simple_container_fixed import container
from src.genesis.core.settings import settings
from src.genesis.core.middleware import RequestIdMiddleware, TimingMiddleware
from src.genesis.infrastructure.database.manager import get_db_session
from fastapi import Response
from apps.rest_api.v1.routers._debug_router_fixed import router as debug_router
from apps.rest_api.v1.routers.llm_router import router as llm_router
from apps.rest_api.v1.routers.mcp_router import router as mcp_router

# ✅ 关键修复: 导入 ai_tools 包，这将触发 __init__.py 中的工具自动注册。
# 这一行导入是为了执行工具注册的"副作用"，即使这里没有直接使用 `ai_tools` 变量。
from src.genesis import ai_tools

# ✅ 已修复: SimpleQwenService 已移除，现在使用 infrastructure/llm/qwen_service.py 中的服务
# 避免重复实现和潜在的配置冲突


def setup_logging():
    """设置日志配置"""
    try:
        config_path = Path("logging_config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            print("日志配置加载成功")
        else:
            print("日志配置文件不存在，使用默认配置")
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    except Exception as e:
        print(f"日志配置失败: {e}")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化资源
    
    # 1. 设置日志
    setup_logging()
    logger = logging.getLogger("genesis")
    logger.info("正在启动 Genesis AI 应用...")
    
    # 2. 验证工具注册（由于导入了ai_tools包，工具应该已经自动注册）
    try:
        from src.genesis.ai_tools.registry import tool_registry
        registered_tools = tool_registry.get_all_schemas()
        logger.info("已自动注册 %d 个AI工具: %s", 
                   len(registered_tools), 
                   [tool['function']['name'] for tool in registered_tools])
    except Exception as e:
        logger.warning("AI工具注册验证失败: %s", e)
    
    # 3. 初始化数据库
    try:
        from src.genesis.infrastructure.database.manager import initialize_db
        from src.genesis.core.settings import settings
        
        db_manager = await initialize_db(settings.database)
        logger.info("数据库初始化完成")
        
        # 将db_manager存储在app状态中
        app.state.db_manager = db_manager
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("正在关闭 Genesis AI 应用...")
    try:
        if hasattr(app.state, 'db_manager'):
            await app.state.db_manager.close()
        logger.info("应用已安全关闭")
    except Exception as e:
        logger.error(f"关闭应用时出错: {e}")

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Genesis AI App",
    version="1.0.0",
    description="企业级AI应用启动模板",
    debug=settings.app.debug,
    lifespan=lifespan,
    
    # OpenAPI 文档配置
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 添加中间件 (顺序很重要)
app.add_middleware(RequestIdMiddleware)  # 最外层，生成请求ID
app.add_middleware(TimingMiddleware)     # 性能监控

# 数据库会话清理中间件
@app.middleware("http")
async def db_session_cleanup_middleware(request: Request, call_next):
    """数据库会话清理中间件"""
    response = await call_next(request)
    
    # 清理数据库会话
    if hasattr(get_db_session, '_session_contexts'):
        # 获取当前请求的所有会话上下文
        sessions_to_close = list(get_db_session._session_contexts.items())
        
        # 清理所有会话
        for session_id, session_context in sessions_to_close:
            try:
                await session_context.__aexit__(None, None, None)
                del get_db_session._session_contexts[session_id]
            except Exception as e:
                # 忽略清理时的错误
                pass
    
    return response

# 包含路由器 - 使用标准API路径格式
app.include_router(debug_router, prefix="/api/v1")
app.include_router(llm_router, prefix="/api/v1")
app.include_router(mcp_router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    """根路径端点"""
    return {
        "message": "Hello World from Genesis AI App!",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health(request: Request):
    """健康检查端点"""
    # 检查数据库连接状态
    db_status = "unknown"
    try:
        db_manager = request.app.state.db_manager
        db_healthy = await db_manager.health_check()
        db_status = "healthy" if db_healthy else "unhealthy"
        pool_status = db_manager.get_pool_status() if db_healthy else {}
    except Exception:
        db_status = "error"
        pool_status = {}
    
    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "message": "Application is running",
        "timestamp": datetime.utcnow().isoformat(),
        "app": {
            "name": "Genesis AI App",
            "version": "1.0.0",
            "environment": settings.env
        },
        "database": {
            "status": db_status,
            "pool": pool_status
        }
    }

# ✅ 已清理：移除了信息接口和测试接口，保持代码简洁
# 相关功能可通过调试接口获取

# ✅ 已修复: LLM相关模型和功能已移至 apps/rest_api/v1/routers/llm_router.py
# 避免重复定义和潜在的冲突

# ✅ 已修复: 移除重复的千问服务实例，现在通过依赖注入使用统一的服务

# ✅ 已修复: 移除了冲突的旧LLM端点，现在统一使用llm_router中的工具调用端点
# 相关的LLM功能已移至 apps/rest_api/v1/routers/llm_router.py

# 导出应用实例供外部使用
__all__ = ["app"]
