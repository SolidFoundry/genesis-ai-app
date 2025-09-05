"""
Genesis AI 应用数据库会话服务
===========================

本模块提供基于数据库的会话管理功能，包括：
- 会话创建和管理
- 智能历史记录获取（带工具调用链保护）
- 消息历史更新

参考 py-ai-core 项目的实现，针对当前项目优化。
"""

import logging
import json
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from src.genesis.infrastructure.database.models import ChatMessage, ChatSession
from src.genesis.core.settings import settings

logger = logging.getLogger(__name__)


class SessionService:
    """数据库会话服务"""
    
    def __init__(self):
        """初始化会话服务"""
        logger.info("数据库会话服务 (SessionService) 已初始化。")

    async def get_or_create_session(
        self, session_id: str, db: AsyncSession
    ) -> ChatSession:
        """获取或创建一个会话对象"""
        query = select(ChatSession).where(ChatSession.session_id == session_id)
        result = await db.execute(query)
        session = result.scalars().first()

        if not session:
            logger.info("会话 '%s' 不存在，正在创建新会话...", session_id)
            session = ChatSession(
                session_id=session_id, 
                system_prompt=settings.llm.default_system_prompt
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            logger.info("新会话 '%s' 已成功创建并使用默认系统提示词。", session_id)
        return session

    async def get_or_create_session_prompt(
        self, session_id: str, db: AsyncSession, requested_prompt: Optional[str] = None
    ) -> str:
        """
        获取会话的系统提示词。如果请求中提供了新的提示词，则更新会话。
        """
        session = await self.get_or_create_session(session_id, db)

        if requested_prompt and session.system_prompt != requested_prompt:
            logger.info("为会话 '%s' 更新系统提示词。", session_id)
            session.system_prompt = requested_prompt
            await db.commit()
            await db.refresh(session)
            logger.info("会话 '%s' 的系统提示词已更新。", session_id)

        return session.system_prompt or settings.llm.default_system_prompt

    async def get_history(
        self, session_id: str, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        根据 session_id 从数据库获取历史消息。
        实现了"智能滑动窗口"机制，确保工具调用链的完整性。
        """
        if not session_id:
            return []

        logger.info("正在从数据库为会话 '%s' 获取历史记录 (智能截断)...", session_id)

        # 1. 为了保证逻辑完整性，我们稍微多取一些数据，比如窗口大小的两倍
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at), desc(ChatMessage.id))
            .limit(settings.llm.max_history_messages * 2)  # 多取一些作为缓冲区
        )

        result = await db.execute(query)
        # 注意：这里是倒序的，最新的在最前面
        recent_messages_desc = result.scalars().all()

        if not recent_messages_desc:
            logger.info("会话 '%s' 在数据库中没有历史记录。", session_id)
            return []

        # 2. 从最新的消息开始，截取到我们配置的窗口大小
        if len(recent_messages_desc) > settings.llm.max_history_messages:
            truncated_desc = recent_messages_desc[:settings.llm.max_history_messages]
        else:
            truncated_desc = recent_messages_desc

        # 3. ✅✅✅ 智能截断的核心逻辑 ✅✅✅
        #    检查被截断后的"最老"一条消息（在倒序列表里是最后一条）
        #    如果它是一个 'tool' 或者是有 'tool_calls' 的 'assistant' 消息，
        #    说明一个完整的调用链被切断了，我们需要往前多取几条，直到找到这个链的起点。
        final_messages_desc = list(truncated_desc)

        # 从被截断的边缘开始往回看
        oldest_message_in_window_index = len(truncated_desc) - 1

        # 只要窗口的最老一条消息是工具调用链的一部分，就继续往前扩张窗口
        while oldest_message_in_window_index < len(recent_messages_desc) - 1:
            oldest_message_model = final_messages_desc[-1]
            try:
                # 解析消息内容来判断
                content_dict = json.loads(oldest_message_model.content)
                role = content_dict.get("role")
                has_tool_calls = "tool_calls" in content_dict

                # 如果最老的消息是 tool，或者是有 tool_calls 的 assistant，说明链条不完整
                if role == "tool" or (role == "assistant" and has_tool_calls):
                    logger.debug("发现不完整的工具调用链，正在向前扩展历史窗口...")
                    # 从原始的、更长的历史记录中，把更早的一条消息加进来
                    oldest_message_in_window_index += 1
                    final_messages_desc.append(
                        recent_messages_desc[oldest_message_in_window_index]
                    )
                else:
                    # 如果最老的消息是 user 或者普通的 assistant 回答，说明链条是完整的，可以停止扩展
                    break
            except (json.JSONDecodeError, AttributeError):
                # 解析失败或格式不对，也视为一个完整的终点
                break

        # 4. 将最终确定的、倒序的消息列表，反转成正确的对话顺序
        messages_in_correct_order = list(reversed(final_messages_desc))

        logger.info(
            "成功获取会话 '%s' 的 %d 条历史消息 (原始上限: %d, 智能扩展后)。",
            session_id,
            len(messages_in_correct_order),
            settings.llm.max_history_messages,
        )

        history_dicts = []
        for msg in messages_in_correct_order:
            try:
                message_dict = json.loads(msg.content)
                history_dicts.append(message_dict)
            except json.JSONDecodeError:
                logger.warning("解析历史消息 content 失败，消息ID: %s", msg.id)
                history_dicts.append({"role": msg.role, "content": msg.content})

        return history_dicts

    async def update_history(
        self, session_id: str, new_messages: List[Dict[str, Any]], db: AsyncSession
    ):
        """
        向数据库中为指定 session_id 写入新的消息。
        """
        if not session_id or not new_messages:
            return

        logger.info(
            "正在为会话 '%s' 向数据库写入 %d 条新消息...", session_id, len(new_messages)
        )

        db_messages = []
        for msg in new_messages:
            content_str = json.dumps(msg, ensure_ascii=False)
            role = msg.get("role", "unknown")
            db_messages.append(
                ChatMessage(session_id=session_id, role=role, content=content_str)
            )

        db.add_all(db_messages)
        await db.commit()
        logger.info(
            "成功为会话 '%s' 写入了 %d 条新消息。", session_id, len(db_messages)
        )

    async def clear_session(self, session_id: str, db: AsyncSession) -> bool:
        """清除指定会话的所有历史记录"""
        try:
            # 删除所有消息
            delete_messages_query = select(ChatMessage).where(ChatMessage.session_id == session_id)
            result = await db.execute(delete_messages_query)
            messages_to_delete = result.scalars().all()
            
            for message in messages_to_delete:
                await db.delete(message)
            
            await db.commit()
            logger.info("已清除会话 '%s' 的所有历史记录", session_id)
            return True
        except Exception as e:
            logger.error("清除会话 '%s' 历史记录失败: %s", session_id, str(e))
            await db.rollback()
            return False

    async def list_sessions(self, db: AsyncSession, limit: int = 100) -> List[str]:
        """列出所有会话ID"""
        try:
            query = select(ChatSession.session_id).order_by(desc(ChatSession.created_at)).limit(limit)
            result = await db.execute(query)
            sessions = result.scalars().all()
            return [session_id for session_id in sessions]
        except Exception as e:
            logger.error("获取会话列表失败: %s", str(e))
            return []


# 创建全局单例
session_service = SessionService()


# 导出服务实例
__all__ = ["session_service", "SessionService"]