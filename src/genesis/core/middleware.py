"""
Genesis AI 应用中间件模块
==========================

本模块提供各种中间件实现，包括：
- 请求ID生成和追踪
- 性能监控和耗时统计
- 日志记录
- 错误处理
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """请求ID中间件，为每个请求生成唯一ID"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始
        start_time = time.time()
        access_logger = logging.getLogger("genesis.access")
        
        access_logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else ""
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算耗时
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # 记录请求完成
            access_logger.info(
                f"请求已处理: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "duration": duration_ms
                }
            )
            
            # 在响应头中添加请求ID
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 记录请求异常
            duration_ms = round((time.time() - start_time) * 1000, 2)
            access_logger.error(
                f"请求处理失败: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "duration": duration_ms
                },
                exc_info=True
            )
            raise


class TimingMiddleware(BaseHTTPMiddleware):
    """性能监控中间件，记录请求耗时"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("genesis.performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 记录性能日志
            if hasattr(request.state, 'request_id'):
                self.logger.info(
                    f"性能监控: {request.method} {request.url.path}",
                    extra={
                        "request_id": request.state.request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "processing_time": round(processing_time, 4),
                        "status_code": response.status_code
                    }
                )
            
            # 在响应头中添加处理时间
            response.headers["X-Processing-Time"] = f"{processing_time:.4f}"
            
            return response
            
        except Exception as e:
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 记录性能日志
            if hasattr(request.state, 'request_id'):
                self.logger.error(
                    f"性能监控: 请求处理失败 - {request.method} {request.url.path}",
                    extra={
                        "request_id": request.state.request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "processing_time": round(processing_time, 4),
                        "error": str(e)
                    },
                    exc_info=True
                )
            
            # 重新抛出异常
            raise


# 导出中间件类
__all__ = [
    'RequestIdMiddleware',
    'TimingMiddleware'
]