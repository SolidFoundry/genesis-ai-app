"""
Genesis AI 应用 LLM 提供商接口
===============================

本模块定义了大语言模型提供商的统一接口，支持多种LLM服务。
所有具体的LLM提供商实现都应该遵循这个接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class LLMProviderInterface(ABC):
    """
    大语言模型提供商接口
    
    定义了所有LLM提供商必须实现的方法，确保应用可以
    无缝切换不同的LLM服务提供商。
    """
    
    @abstractmethod
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
            messages: 消息列表，格式为 [{"role": "user", "content": "Hello"}, ...]
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大令牌数
            **kwargs: 其他提供商特定参数
            
        Returns:
            包含响应结果的字典
        """
        pass
    
    @abstractmethod
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
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数
            max_tokens: 最大令牌数
            **kwargs: 其他提供商特定参数
            
        Returns:
            生成的文本内容
        """
        pass
    
    @abstractmethod
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表
        
        Returns:
            模型信息列表
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取特定模型的信息
        
        Args:
            model: 模型名称
            
        Returns:
            模型详细信息
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            如果服务正常返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        获取提供商名称
        
        Returns:
            提供商名称
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        获取默认模型名称
        
        Returns:
            默认模型名称
        """
        pass


class LLMProviderException(Exception):
    """LLM提供商异常"""
    pass


class LLMProviderRateLimitError(LLMProviderException):
    """LLM提供商限流错误"""
    pass


class LLMProviderAuthenticationError(LLMProviderException):
    """LLM提供商认证错误"""
    pass


class LLMProviderServiceUnavailableError(LLMProviderException):
    """LLM提供商服务不可用错误"""
    pass


# 导出接口和异常类
__all__ = [
    "LLMProviderInterface",
    "LLMProviderException",
    "LLMProviderRateLimitError", 
    "LLMProviderAuthenticationError",
    "LLMProviderServiceUnavailableError",
]