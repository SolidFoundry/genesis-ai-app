"""
Genesis AI 应用通用工具包
==========================

这个模块包含各种通用的工具函数，可以被大模型调用。
所有工具都使用 @tool 装饰器进行注册，并支持中文日志记录。
"""

import logging
from datetime import datetime
import json
import math
from typing import Any

from src.genesis.ai_tools.registry import tool

logger = logging.getLogger(__name__)


@tool
async def get_current_datetime() -> str:
    """获取当前服务器的日期和时间。

    这个工具非常简单，不需要任何参数。
    它会返回一个格式化好的字符串，表示当前的日期和时间。

    :return: 格式为 'YYYY-MM-DD HH:MM:SS' 的日期时间字符串。
    """
    logger.info("正在执行工具 [get_current_datetime]。")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("工具 [get_current_datetime] 执行成功，返回: %s", current_time)

    return current_time


@tool
async def get_current_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的当前天气信息。

    这是工具的详细描述，可以有多行。
    第一行通常作为简短描述。

    :param city: 必要参数，需要获取天气的城市名称，例如 "北京"。
    :param unit: 可选参数，温度单位，可以是 "celsius" 或 "fahrenheit"，默认为 "celsius"。
    :return: 描述天气信息的字符串。
    """
    logger.info(
        "正在执行工具 [get_current_weather]，参数: city='%s', unit='%s'", city, unit
    )

    # 模拟实际的 API 调用。在真实场景中，这里会有网络请求。
    try:
        # 这是一个模拟的返回结果
        weather_info = f"{city}的天气是晴朗, 30度 {unit}."
        logger.info("工具 [get_current_weather] 执行成功，返回: %s", weather_info)
        return weather_info
    except Exception as e:
        logger.exception("执行工具 [get_current_weather] 时发生未知错误。")
        # 向上抛出异常或返回一个错误信息
        return f"获取 {city} 天气时发生错误: {e}"


@tool
async def calculate(expression: str) -> str:
    """计算数学表达式的结果。

    支持基本的数学运算，包括加减乘除、幂运算等。
    
    :param expression: 要计算的数学表达式，例如 "2 + 3 * 4" 或 "sqrt(16)"。
    :return: 计算结果的字符串表示。
    """
    logger.info("正在执行工具 [calculate]，参数: expression='%s'", expression)
    
    try:
        # 安全的数学表达式计算
        # 只允许特定的数学函数和操作符
        allowed_names = {
            k: v for k, v in math.__dict__.items() 
            if not k.startswith("_")
        }
        
        # 编译表达式
        code = compile(expression, "<string>", "eval")
        
        # 验证表达式安全性
        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"不允许使用函数或变量: {name}")
        
        # 计算结果
        result = eval(code, {"__builtins__": {}}, allowed_names)
        
        logger.info("工具 [calculate] 执行成功，表达式 '%s' 的结果: %s", expression, result)
        return f"计算结果: {result}"
        
    except Exception as e:
        logger.error("工具 [calculate] 执行失败，表达式 '%s' 错误: %s", expression, str(e))
        return f"计算失败: {str(e)}"


@tool
async def get_system_info() -> str:
    """获取系统基本信息。

    返回当前系统的基本信息，包括时间、Python版本等。
    
    :return: 系统信息的JSON格式字符串。
    """
    logger.info("正在执行工具 [get_system_info]。")
    
    try:
        import platform
        import sys
        
        system_info = {
            "系统": platform.system(),
            "系统版本": platform.version(),
            "机器架构": platform.machine(),
            "Python版本": sys.version,
            "当前时间": datetime.now().isoformat(),
        }
        
        result = json.dumps(system_info, ensure_ascii=False, indent=2)
        logger.info("工具 [get_system_info] 执行成功。")
        return result
        
    except Exception as e:
        logger.exception("执行工具 [get_system_info] 时发生未知错误。")
        return f"获取系统信息时发生错误: {e}"


@tool
async def search_web(query: str, num_results: int = 5) -> str:
    """模拟网络搜索功能。

    注意：这是一个模拟工具，返回模拟的搜索结果。
    
    :param query: 搜索关键词。
    :param num_results: 返回结果数量，默认为5。
    :return: 搜索结果的字符串表示。
    """
    logger.info("正在执行工具 [search_web]，参数: query='%s', num_results=%d", query, num_results)
    
    try:
        # 模拟搜索结果
        mock_results = [
            {
                "标题": f"关于 '{query}' 的搜索结果 {i+1}",
                "链接": f"https://example.com/result{i+1}",
                "摘要": f"这是关于 '{query}' 的第{i+1}个搜索结果的摘要内容..."
            }
            for i in range(min(num_results, 10))
        ]
        
        result = json.dumps(mock_results, ensure_ascii=False, indent=2)
        logger.info("工具 [search_web] 执行成功，返回 %d 个结果。", len(mock_results))
        return result
        
    except Exception as e:
        logger.exception("执行工具 [search_web] 时发生未知错误。")
        return f"搜索失败: {e}"