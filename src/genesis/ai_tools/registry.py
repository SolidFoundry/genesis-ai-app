import inspect
import json
import logging
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)

TYPE_MAPPING = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}


class ToolRegistry:
    def __init__(self):
        """工具注册中心构造函数"""
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        logger.info("工具注册中心 (ToolRegistry) 已初始化。")

    def register(self, func: Callable):
        """
        注册一个新工具，并根据其签名和文档字符串生成 schema。
        """
        tool_name = func.__name__

        logger.info("开始注册新工具：%s", tool_name)

        self.tools[tool_name] = func

        # --- 生成 Schema ---
        sig = inspect.signature(func)
        doc = inspect.getdoc(func)
        description = doc.split("\n")[0] if doc else ""

        logger.debug("工具 '%s' 的描述: '%s'", tool_name, description)

        parameters = {"type": "object", "properties": {}, "required": []}
        for name, param in sig.parameters.items():
            param_type = TYPE_MAPPING.get(param.annotation.__name__, "string")
            parameters["properties"][name] = {
                "type": param_type,
                "description": f"参数: {name}",
            }
            if param.default is inspect.Parameter.empty:
                parameters["required"].append(name)

        logger.debug("为工具 '%s' 生成的参数 schema: %s", tool_name, parameters)

        tool_schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
            },
        }
        self.tool_schemas.append(tool_schema)

        logger.info("工具 '%s' 已成功注册并生成 schema。", tool_name)

        return func

    def get_tool(self, name: str) -> Callable | None:
        """根据名称获取已注册的工具函数"""
        tool = self.tools.get(name)
        if tool:
            logger.debug("成功获取工具: %s", name)
        else:
            logger.warning("尝试获取一个未注册的工具: %s", name)
        return tool

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """获取所有已注册工具的 schema 列表"""
        logger.debug(
            "正在获取所有已注册工具的 schema，共 %d 个。", len(self.tool_schemas)
        )
        return self.tool_schemas


# 实例化对象
tool_registry = ToolRegistry()


# 装饰器函数
def tool(func: Callable):
    """
    一个用于注册工具的装饰器。
    用法:
    @tool
    def my_function(...):
        ...
    """
    return tool_registry.register(func)