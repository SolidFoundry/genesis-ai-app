"""
Genesis AI 应用数据库基础设施模块
================================

本模块提供数据库相关的所有基础设施功能：
- 连接池管理
- ORM 基类定义
- 数据模型
- 会话管理
- 事务支持
"""

from .manager import (
    Base,
    DatabaseManager,
    get_db_manager,
    initialize_db,
    close_db,
    get_db_session,
    get_db_transaction,
)

from .models import (
    UserSession,
    UserBehavior,
    IntentAnalysis,
    AdRecommendation,
    ChatSession,
    ChatMessage,
    SystemConfig,
    LLMCall,
    APILog,
)

__all__ = [
    # 基础设施
    "Base",
    "DatabaseManager",
    "get_db_manager", 
    "initialize_db",
    "close_db",
    "get_db_session",
    "get_db_transaction",
    # 数据模型
    "UserSession",
    "UserBehavior",
    "IntentAnalysis",
    "AdRecommendation",
    "ChatSession",
    "ChatMessage",
    "SystemConfig",
    "LLMCall",
    "APILog",
]