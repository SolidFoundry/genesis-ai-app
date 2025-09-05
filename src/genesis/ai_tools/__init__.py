"""
AI工具模块
==========

本模块自动注册所有可用的AI工具。
"""

# 导入所有工具，这样它们就会被自动注册
from .tools.math_tools import calculate
from .general_tools import (
    get_current_datetime,
    get_current_weather,
    calculate as general_calculate,
    get_system_info,
    search_web
)

# 导出工具注册中心和装饰器
from .registry import tool_registry, tool

__all__ = [
    "tool_registry", 
    "tool", 
    "calculate",
    "get_current_datetime",
    "get_current_weather", 
    "general_calculate",
    "get_system_info",
    "search_web"
]