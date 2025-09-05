"""
Genesis AI 应用 Qwen 提供商
============================

本模块实现阿里云通义千问 API 的 LLM 提供商，遵循 LLMProviderInterface 接口。
支持聊天补全、文本生成、模型查询等功能。
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from src.genesis.core.settings import LLMProviderConfig
from ..interface import (
    LLMProviderInterface,
    LLMProviderException,
    LLMProviderRateLimitError,
    LLMProviderAuthenticationError,
    LLMProviderServiceUnavailableError,
)


class QwenChatMessage(BaseModel):
    """Qwen 聊天消息模型"""
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")


class QwenChatCompletionRequest(BaseModel):
    """Qwen 聊天补全请求模型"""
    model: str = Field(..., description="模型名称")
    messages: List[QwenChatMessage] = Field(..., description="消息列表")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大令牌数")
    stream: Optional[bool] = Field(False, description="是否流式输出")


class QwenChatCompletionResponse(BaseModel):
    """Qwen 聊天补全响应模型"""
    id: str = Field(..., description="响应ID")
    object: str = Field(..., description="对象类型")
    created: int = Field(..., description="创建时间")
    model: str = Field(..., description="使用的模型")
    choices: List[Dict[str, Any]] = Field(..., description="选择列表")
    usage: Optional[Dict[str, int]] = Field(None, description="使用统计")


class QwenProvider(LLMProviderInterface):
    """
    Qwen 提供商实现
    
    使用阿里云通义千问 API 提供大语言模型服务。
    """
    
    def __init__(self, config: LLMProviderConfig, http_client: Optional[httpx.AsyncClient] = None):
        """
        初始化 Qwen 提供商
        
        Args:
            config: Qwen 配置
            http_client: HTTP客户端，如果为None则创建新的
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        
        # 创建HTTP客户端
        self._http_client = http_client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._get_api_key()}",
            },
        )
    
    def _get_api_key(self) -> str:
        """获取API密钥"""
        # 从环境变量获取Qwen API密钥
        import os
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise LLMProviderAuthenticationError("Qwen API密钥未配置，请设置 QWEN_API_KEY 环境变量")
        return api_key
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行聊天补全请求
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Returns:
            聊天补全响应
        """
        try:
            # 构建请求数据
            request_data = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
                **kwargs
            }
            
            # 发送请求
            response = await self._http_client.post(
                "/chat/completions",
                json=request_data,
            )
            
            # 检查响应状态
            if response.status_code == 401:
                raise LLMProviderAuthenticationError("Qwen API认证失败")
            elif response.status_code == 429:
                raise LLMProviderRateLimitError("Qwen API请求频率限制")
            elif response.status_code >= 500:
                raise LLMProviderServiceUnavailableError("Qwen服务不可用")
            elif response.status_code != 200:
                raise LLMProviderException(f"Qwen API请求失败: {response.status_code}")
            
            # 解析响应
            response_data = response.json()
            return response_data
            
        except httpx.TimeoutException:
            raise LLMProviderServiceUnavailableError("Qwen API请求超时")
        except httpx.NetworkError as e:
            raise LLMProviderServiceUnavailableError(f"Qwen API网络错误: {e}")
        except Exception as e:
            if isinstance(e, LLMProviderException):
                raise
            raise LLMProviderException(f"Qwen API请求异常: {e}")
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        # 将prompt转换为消息格式
        messages = [{"role": "user", "content": prompt}]
        
        # 调用聊天补全
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 提取生成的文本
        choices = response.get("choices", [])
        if not choices:
            raise LLMProviderException("Qwen API返回空响应")
        
        message = choices[0].get("message", {})
        content = message.get("content", "")
        
        return content
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表
        
        Returns:
            模型信息列表
        """
        try:
            response = await self._http_client.get("/models")
            
            if response.status_code != 200:
                raise LLMProviderException(f"获取模型列表失败: {response.status_code}")
            
            data = response.json()
            models = data.get("data", [])
            
            # 转换为标准格式
            result = []
            for model in models:
                result.append({
                    "id": model.get("id"),
                    "object": model.get("object"),
                    "created": model.get("created"),
                    "owned_by": model.get("owned_by"),
                })
            
            return result
            
        except Exception as e:
            if isinstance(e, LLMProviderException):
                raise
            raise LLMProviderException(f"获取模型列表异常: {e}")
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取特定模型的信息
        
        Args:
            model: 模型名称
            
        Returns:
            模型详细信息
        """
        # 获取所有模型
        models = await self.get_models()
        
        # 查找指定模型
        for model_info in models:
            if model_info["id"] == model:
                return model_info
        
        raise LLMProviderException(f"模型不存在: {model}")
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            如果服务正常返回True，否则返回False
        """
        try:
            # 尝试获取模型列表作为健康检查
            await self.get_models()
            return True
        except Exception:
            return False
    
    def get_provider_name(self) -> str:
        """
        获取提供商名称
        
        Returns:
            提供商名称
        """
        return "qwen"
    
    def get_default_model(self) -> str:
        """
        获取默认模型名称
        
        Returns:
            默认模型名称
        """
        return self.model
    
    async def close(self):
        """关闭HTTP客户端"""
        if self._http_client:
            await self._http_client.aclose()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# 导出Qwen提供商
__all__ = ["QwenProvider"]