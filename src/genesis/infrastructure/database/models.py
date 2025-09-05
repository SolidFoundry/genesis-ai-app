"""
Genesis AI 应用数据库模型
=======================

本模块定义了应用的所有数据库表模型，包括：
- 用户和会话管理
- 聊天和消息数据
- LLM调用和工具使用
- 业务逻辑和推荐系统
- 系统配置和监控

参考 Heimdall 项目的数据库设计，针对AI应用场景优化。
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, func, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.genesis.infrastructure.database.manager import Base


class User(Base):
    """
    用户数据模型，对应 'users' 表。
    用于存储用户账户信息。
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserSession(Base):
    """
    用户会话数据模型，对应 'user_sessions' 表。
    用于存储用户会话的元数据，包括用户信息和会话设定。
    """

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 会话和用户信息
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 用户画像信息
    user_segment = Column(String(100), nullable=True)  # 用户分群
    preferences = Column(JSON, nullable=True)  # 用户偏好设置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<UserSession(id={self.id}, session_id='{self.session_id}', user_id='{self.user_id}')>"


class UserBehavior(Base):
    """
    用户行为数据模型，对应 'user_behaviors' 表。
    用于存储用户的行为历史记录，如浏览、搜索、点击等。
    """

    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 行为类型和内容
    behavior_type = Column(String(50), nullable=False)  # 'view', 'search', 'click', 'purchase'
    behavior_data = Column(JSON, nullable=False)  # 行为的具体数据
    
    # 意图分析结果
    detected_intent = Column(String(255), nullable=True)
    intent_confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserBehavior(id={self.id}, session_id='{self.session_id}', type='{self.behavior_type}')>"


class IntentAnalysis(Base):
    """
    意图分析结果数据模型，对应 'intent_analyses' 表。
    用于存储AI对用户意图的分析结果。
    """

    __tablename__ = "intent_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 意图分析结果
    primary_intent = Column(String(255), nullable=False)
    secondary_intents = Column(JSON, nullable=True)  # 次要意图列表
    target_audience_segment = Column(String(100), nullable=False)
    urgency_level = Column(Float, nullable=False)  # 0.0 到 1.0
    
    # 分析元数据
    analysis_model = Column(String(100), nullable=True)  # 使用的AI模型
    analysis_confidence = Column(Float, nullable=True)  # 整体置信度
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<IntentAnalysis(id={self.id}, session_id='{self.session_id}', intent='{self.primary_intent}')>"


class AdRecommendation(Base):
    """
    广告推荐数据模型，对应 'ad_recommendations' 表。
    用于存储为用户生成的广告推荐结果。
    """

    __tablename__ = "ad_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    analysis_id = Column(Integer, nullable=True)  # 关联的意图分析ID
    
    # 推荐内容
    ad_id = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False)
    relevance_score = Column(Float, nullable=False)  # 相关性评分 0.0 到 1.0
    ad_copy = Column(Text, nullable=False)  # 推荐的广告文案
    
    # 推荐元数据
    recommendation_reason = Column(Text, nullable=True)  # 推荐理由
    position = Column(Integer, nullable=True)  # 推荐位置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AdRecommendation(id={self.id}, ad_id='{self.ad_id}', score={self.relevance_score})>"


class ChatSession(Base):
    """
    聊天会话数据模型，对应 'chat_sessions' 表。
    用于存储聊天会话的元数据，包括系统提示词等。
    """

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    system_prompt = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}')>"


class ChatMessage(Base):
    """
    聊天消息数据模型，对应 'chat_messages' 表。
    用于存储聊天对话的消息历史。
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'tool', 'system'
    content = Column(Text, nullable=False)  # JSON格式的消息内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}', role='{self.role}')>"


class SystemConfig(Base):
    """
    系统配置数据模型，对应 'system_config' 表。
    用于存储系统的配置参数。
    """

    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.key}', value='{self.value[:50]}...')>"


class LLMCall(Base):
    """
    LLM调用记录数据模型，对应 'llm_calls' 表。
    用于记录所有大语言模型的调用情况。
    """

    __tablename__ = "llm_calls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=True)
    user_id = Column(String(255), index=True, nullable=True)
    
    # 调用信息
    provider = Column(String(50), nullable=False)  # 'openai', 'qwen', etc.
    model = Column(String(100), nullable=False)
    endpoint = Column(String(100), nullable=False)
    
    # 请求和响应
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    
    # 性能指标
    latency_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LLMCall(id={self.id}, provider='{self.provider}', model='{self.model}', status={self.status_code})>"


class APILog(Base):
    """
    API调用日志数据模型，对应 'api_logs' 表。
    用于记录所有API请求的日志信息。
    """

    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), index=True, nullable=False)
    session_id = Column(String(255), index=True, nullable=True)
    user_id = Column(String(255), index=True, nullable=True)
    
    # 请求信息
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    query_params = Column(JSON, nullable=True)
    headers = Column(JSON, nullable=True)
    body = Column(Text, nullable=True)
    
    # 响应信息
    status_code = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=True)
    
    # 性能指标
    latency_ms = Column(Integer, nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<APILog(id={self.id}, method='{self.method}', path='{self.path}', status={self.status_code})>"


class ToolCall(Base):
    """
    工具调用记录数据模型，对应 'tool_calls' 表。
    用于记录所有工具的调用情况。
    """

    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=True)
    tool_name = Column(String(100), nullable=False)
    tool_args = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)  # 'success', 'error'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool_name='{self.tool_name}', status='{self.status}')>"


class PerformanceMetric(Base):
    """
    性能指标数据模型，对应 'performance_metrics' 表。
    用于存储系统的性能监控数据。
    """

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 6), nullable=False)
    tags = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PerformanceMetric(id={self.id}, name='{self.metric_name}', value={self.metric_value})>"


class ErrorLog(Base):
    """
    错误日志数据模型，对应 'error_logs' 表。
    用于记录所有系统错误信息。
    """

    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type='{self.error_type}', message='{self.error_message[:50]}...')>"


class AuditLog(Base):
    """
    审计日志数据模型，对应 'audit_logs' 表。
    用于记录所有系统操作的审计信息。
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    changes = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"


# 导出所有模型
__all__ = [
    "User",
    "UserSession",
    "UserBehavior", 
    "IntentAnalysis",
    "AdRecommendation",
    "ChatSession",
    "ChatMessage",
    "SystemConfig",
    "LLMCall",
    "APILog",
    "ToolCall",
    "PerformanceMetric",
    "ErrorLog",
    "AuditLog",
]