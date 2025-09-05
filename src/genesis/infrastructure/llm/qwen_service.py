"""
千问大模型服务模块
=================

本模块提供与千问大模型的交互功能，基于用户提供的代码片段实现。
支持工具调用和会话记忆功能。
"""

import logging
import os
import json
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from src.genesis.core.settings import settings

logger = logging.getLogger(__name__)


class QwenLLMService:
    def __init__(self):
        """
        构造函数，初始化与千问大模型服务的异步客户端。
        """
        logger.info("正在初始化千问大模型服务 (QwenLLMService)...")

        # Get API key and base URL from settings
        api_key = settings.openai_api_key or settings.llm.api_key or settings.llm.qwen_api_key
        api_base = settings.openai_api_base or settings.llm.api_base or settings.llm.external_api_llm_base_url
        model_name = settings.model_name or settings.llm.model_name or "qwen-max"

        if not api_key or not api_base:
            logger.error(
                "关键配置 LLM_API_KEY 或 LLM_API_BASE 未设置！服务可能无法正常工作。"
            )

        self.client = AsyncOpenAI(
            api_key=api_key, base_url=api_base
        )
        logger.info(
            "千问大模型服务客户端已成功创建，目标地址: %s", api_base
        )

    def _get_client(self):
        """
        获取或重新创建配置正确的OpenAI客户端
        """
        # 检查配置是否有效 - 支持多个配置字段
        api_key = settings.openai_api_key or settings.llm.api_key or settings.llm.qwen_api_key
        api_base = settings.openai_api_base or settings.llm.api_base or settings.llm.external_api_llm_base_url
        
        if not api_key or not api_base:
            logger.error("LLM服务配置缺失: API_KEY或API_BASE未设置")
            raise ValueError("LLM服务配置缺失")
        
        # 检查客户端是否存在且配置正确
        if (not hasattr(self, 'client') or 
            not self.client or 
            not self.client.base_url or 
            not self.client.api_key):
            
            logger.warning("重新创建LLM客户端...")
            
            # 重新创建客户端
            self.client = AsyncOpenAI(
                api_key=api_key, 
                base_url=api_base
            )
            logger.info("LLM客户端已创建，目标地址: %s", api_base)
        
        return self.client

    async def get_model_decision(
        self, messages: List[Dict[str, Any]], tool_schemas: List[Dict[str, Any]]
    ):
        """
        请求大模型，让其根据完整的消息历史决定是直接回答还是调用工具。
        """
        logger.info("正在向千问大模型请求决策...")
        logger.debug(
            "发送给大模型的决策请求内容: messages数量=%d, tools数量=%d", len(messages), len(tool_schemas)
        )
        
        # 详细记录工具schemas信息（便于调试）
        for i, tool_schema in enumerate(tool_schemas):
            logger.debug("工具 %d: %s", i + 1, json.dumps(tool_schema, ensure_ascii=False))

        # 获取配置正确的客户端
        client = self._get_client()
        
        # 记录详细的API调用参数
        model_name = settings.llm.model_name or "qwen-max"
        logger.debug("LLM API调用参数 - 模型: %s, 消息数量: %d, 工具数量: %d", 
                    model_name, len(messages), len(tool_schemas))
        logger.debug("LLM Client配置 - API Key存在: %s, 基础URL: %s", 
                    bool(client.api_key), client.base_url)
        
        # 记录最后一条用户消息
        if messages:
            last_message = messages[-1]
            logger.debug("最后一条消息: 角色=%s, 内容长度=%d", 
                        last_message.get("role", "unknown"), 
                        len(last_message.get("content", "")))

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            model_message = response.choices[0].message
            usage = response.usage.model_dump() if hasattr(response, 'usage') else {}
            
            logger.info("成功从千问大模型获取决策响应。")
            logger.debug("大模型决策响应 - 有工具调用: %s, 内容长度: %d", 
                        bool(getattr(model_message, 'tool_calls', None)), 
                        len(model_message.content or ""))
            logger.debug("API使用统计: %s", usage)
            
            return model_message

        except Exception as e:
            logger.exception("调用千问大模型决策 API 时发生严重错误。")
            raise

    async def get_summary_from_tool_results(
        self,
        messages_for_summary: List[Dict[str, Any]],
    ):
        """
        在工具执行后，将包含工具结果的完整上下文发回给大模型，让其进行总结。
        :param messages_for_summary: 完整的对话历史，包含用户问题、AI思考、工具结果等。
        :return: 大模型生成的最终总结性回复字符串。
        """
        logger.info("正在向千问大模型请求对工具结果进行总结...")
        logger.debug("发送给大模型的总结请求消息数量: %d", len(messages_for_summary))

        # 获取配置正确的客户端
        client = self._get_client()
        
        model_name = settings.llm.model_name or "qwen-max"
        logger.debug("总结API调用参数 - 模型: %s, 消息数量: %d", model_name, len(messages_for_summary))
        logger.debug("LLM Client配置 - API Key存在: %s, 基础URL: %s", 
                    bool(client.api_key), client.base_url)

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages_for_summary,
            )
            summary_content = response.choices[0].message.content
            usage = response.usage.model_dump() if hasattr(response, 'usage') else {}
            
            logger.info("成功从千问大模型获取总结性回复。")
            logger.debug("大模型总结回复 - 内容长度: %d", len(summary_content or ""))
            logger.debug("总结API使用统计: %s", usage)
            
            return summary_content

        except Exception as e:
            logger.exception("调用千问大模型总结 API 时发生严重错误。")
            return "抱歉，我在总结工具执行结果时遇到了一个问题。"

    async def chat_completion(self, **kwargs):
        """
        通用的聊天补全方法，用于直接调用LLM API
        """
        logger.info("正在执行直接千问大模型聊天补全调用...")
        
        # 记录调用参数（排除敏感信息）
        safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['api_key', 'headers']}
        logger.debug("聊天补全调用参数: %s", safe_kwargs)
        
        # 获取配置正确的客户端
        client = self._get_client()
        
        model_name = kwargs.get('model', settings.llm.model_name or "qwen-max")
        messages = kwargs.get('messages', [])
        
        logger.debug("聊天补全API调用参数 - 模型: %s, 消息数量: %d", model_name, len(messages))
        logger.debug("LLM Client配置 - API Key存在: %s, 基础URL: %s", 
                    bool(client.api_key), client.base_url)
        
        try:
            response = await client.chat.completions.create(**kwargs)
            usage = response.usage.model_dump() if hasattr(response, 'usage') else {}
            
            logger.info("成功执行直接千问大模型聊天补全调用。")
            logger.debug("聊天补全响应 - 内容长度: %d", 
                        len(response.choices[0].message.content or "") if response.choices else 0)
            logger.debug("聊天补全API使用统计: %s", usage)
            
            return response
        except Exception as e:
            logger.exception("直接千问大模型聊天补全调用失败。")
            raise


# 创建一个全局单例
qwen_llm_service = QwenLLMService()