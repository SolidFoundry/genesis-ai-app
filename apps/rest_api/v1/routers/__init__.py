"""
Genesis AI 应用 v1 API 路由器
==========================

本模块包含v1版本的所有API路由器。
"""

from ._debug_router_fixed import router as debug_router
from .mcp_router import router as mcp_router

# 导出所有路由器
__all__ = ["debug_router", "mcp_router"]