"""
Genesis AI 应用 LLM 路由器
========================

本模块提供 LLM 相关的 API 端点，包括：
- 大模型对话
- 工具调用
- 记忆功能
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession

from src.genesis.infrastructure.llm.qwen_service import qwen_llm_service
from src.genesis.ai_tools.registry import tool_registry
from src.genesis.core.settings import settings
from src.genesis.infrastructure.database.session_service import session_service
from src.genesis.infrastructure.database.manager import get_db_session
import asyncio

logger = logging.getLogger(__name__)
# 设置日志级别为DEBUG以查看调试信息
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["LLM"])


class LLMWithToolsRequest(BaseModel):
    """LLM 工具调用请求模型"""
    query: str = Field("计算 10 * (3 + 5) / 2", description="用户查询内容")
    session_id: str = Field("test-session-123", description="会话ID")
    system_prompt: Optional[str] = Field("你是一个智能助手，可以使用工具来帮助用户", description="系统提示词")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(2000, description="最大令牌数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "计算 10 * (3 + 5) / 2",
                "session_id": "test-session-123",
                "system_prompt": "你是一个智能助手，可以使用工具来帮助用户",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }


class LLMWithToolsResponse(BaseModel):
    """LLM 工具调用响应模型"""
    success: bool = Field(..., description="是否成功")
    response: str = Field(..., description="模型回复内容")
    session_id: str = Field(..., description="会话ID")
    model_used: str = Field(..., description="使用的模型")
    usage: Optional[Dict[str, Any]] = Field(None, description="使用统计")
    tools_called: Optional[List[Dict[str, Any]]] = Field(None, description="调用的工具")




async def format_messages_with_memory(
    query: str, 
    session_id: str, 
    system_prompt: Optional[str] = None,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """格式化消息，包含数据库历史记忆"""
    messages = []
    
    # 添加系统提示词
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # 从数据库获取历史消息
    if db:
        try:
            history_messages = await session_service.get_history(session_id, db)
            logger.debug("从数据库获取到 %d 条历史消息", len(history_messages))
            
            # 安全验证：确保工具调用链的完整性
            # 使用两阶段处理：先收集所有消息，再验证工具调用链
            valid_messages = []
            
            # 第一阶段：收集所有消息，但跳过孤立的工具消息
            i = 0
            while i < len(history_messages):
                msg = history_messages[i]
                
                # 如果是工具消息，需要验证其完整性
                if msg.get("role") == "tool":
                    # 向前查找对应的assistant消息
                    has_valid_assistant = False
                    for j in range(i - 1, -1, -1):
                        prev_msg = history_messages[j]
                        if (prev_msg.get("role") == "assistant" and 
                            "tool_calls" in prev_msg):
                            # 检查tool_calls是否包含当前tool消息
                            tool_calls = prev_msg["tool_calls"]
                            for tool_call in tool_calls:
                                tool_call_id = tool_call.get("id")
                                tool_name = tool_call.get("function", {}).get("name")
                                
                                # 匹配规则：tool_call_id或tool_name匹配
                                if (tool_call_id and tool_call_id == msg.get("tool_call_id")) or \
                                   (tool_name and tool_name == msg.get("name")):
                                    has_valid_assistant = True
                                    break
                            if has_valid_assistant:
                                break
                    
                    if not has_valid_assistant:
                        logger.warning("发现孤立的工具消息，跳过: %s", msg.get("content", "")[:50])
                        i += 1
                        continue
                
                # 添加消息到验证列表
                valid_messages.append(msg)
                i += 1
            
            # 第二阶段：构建完整的工具调用链
            final_messages = []
            i = 0
            while i < len(valid_messages):
                msg = valid_messages[i]
                
                # 如果是包含tool_calls的assistant消息，需要确保完整的工具调用链
                if msg.get("role") == "assistant" and "tool_calls" in msg:
                    # 收集所有相关的tool消息
                    tool_calls = msg["tool_calls"]
                    tool_responses = []
                    
                    # 向后查找对应的tool消息
                    for j in range(i + 1, len(valid_messages)):
                        next_msg = valid_messages[j]
                        if next_msg.get("role") == "tool":
                            # 检查是否属于当前assistant消息的tool_calls
                            for tool_call in tool_calls:
                                tool_call_id = tool_call.get("id")
                                tool_name = tool_call.get("function", {}).get("name")
                                
                                if (tool_call_id and tool_call_id == next_msg.get("tool_call_id")) or \
                                   (tool_name and tool_name == next_msg.get("name")):
                                    tool_responses.append(next_msg)
                                    break
                        elif next_msg.get("role") in ["user", "assistant"]:
                            # 遇到新的消息，停止收集tool响应
                            break
                    
                    # 只有当所有tool调用都有响应时，才添加完整的工具调用链
                    if len(tool_responses) == len(tool_calls):
                        # 添加assistant消息
                        assistant_msg = {
                            "role": "assistant",
                            "content": msg.get("content", ""),
                            "tool_calls": msg["tool_calls"]
                        }
                        final_messages.append(assistant_msg)
                        
                        # 添加所有tool响应
                        for tool_response in tool_responses:
                            tool_msg = {
                                "role": "tool",
                                "content": tool_response["content"]
                            }
                            if "tool_call_id" in tool_response:
                                tool_msg["tool_call_id"] = tool_response["tool_call_id"]
                            if "name" in tool_response:
                                tool_msg["name"] = tool_response["name"]
                            final_messages.append(tool_msg)
                        
                        # 跳过已处理的tool消息
                        i += len(tool_responses)
                    else:
                        # 工具调用链不完整，跳过整个链
                        logger.warning("工具调用链不完整，跳过: %d 个tool_calls, %d 个响应", 
                                     len(tool_calls), len(tool_responses))
                        # 跳过所有相关的tool消息
                        for j in range(i + 1, len(valid_messages)):
                            if valid_messages[j].get("role") == "tool":
                                i += 1
                            else:
                                break
                
                elif msg.get("role") == "tool":
                    # 孤立的tool消息已经在第一阶段过滤掉了
                    pass
                else:
                    # 普通消息
                    final_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                i += 1
            
            # 使用最终验证的消息列表
            messages.extend(final_messages)
            logger.debug("安全过滤后保留 %d 条历史消息", len(final_messages))
            
        except Exception as e:
            logger.warning("从数据库获取历史消息失败: %s", str(e))
    
    # 添加当前查询
    messages.append({"role": "user", "content": query})
    
    return messages


async def save_to_memory(session_id: str, messages: List[Dict[str, Any]], db):
    """保存消息到数据库"""
    try:
        await session_service.update_history(session_id, messages, db)
        logger.debug("成功保存 %d 条消息到数据库", len(messages))
    except Exception as e:
        logger.error("保存消息到数据库失败: %s", str(e))


@router.post("/llm-with-tools", response_model=LLMWithToolsResponse)
async def llm_with_tools(
    request: LLMWithToolsRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    LLM 工具调用接口
    
    支持大模型对话、工具调用和记忆功能
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    session_id = request.session_id
    
    # 记录详细的请求参数
    logger.info(
        "收到新的LLM工具调用请求，会话ID: '%s'",
        session_id,
        extra={
            "request_id": request_id,
            "session_id": session_id,
            "query_length": len(request.query)
        }
    )
    
    # 记录所有请求参数
    logger.debug(
        "会话 '%s' 的完整请求参数: query='%s', session_id='%s', system_prompt='%s', temperature=%s, max_tokens=%s",
        session_id, request.query, session_id, request.system_prompt, request.temperature, request.max_tokens
    )
    
    try:
        # 1. 准备请求上下文
        logger.debug("会话 '%s': 开始准备请求上下文", session_id)
        
        # 获取工具schemas
        tool_schemas = tool_registry.get_all_schemas()
        logger.debug("会话 '%s': 获取到 %d 个工具schemas", session_id, len(tool_schemas))
        
        # 构建消息历史
        messages = await format_messages_with_memory(
            request.query, 
            session_id, 
            request.system_prompt,
            db
        )
        logger.debug("会话 '%s': 构建了 %d 条历史消息", session_id, len(messages))
        
        # 详细记录构建的消息
        logger.debug("会话 '%s': 构建的消息详情:", session_id)
        for i, msg in enumerate(messages):
            logger.debug(f"  消息 {i}: role={msg.get('role')}, content={msg.get('content', '')[:100]}...")
            if msg.get('role') == 'assistant' and 'tool_calls' in msg:
                logger.debug(f"    tool_calls: {msg['tool_calls']}")
            elif msg.get('role') == 'tool':
                logger.debug(f"    tool_call_id: {msg.get('tool_call_id')}, name: {msg.get('name')}")
        
        # 2. 从LLM获取决策
        logger.info("会话 '%s': 正在请求大模型决策...", session_id)
        logger.debug("发送给LLM的消息用于决策:")
        for i, msg in enumerate(messages):
            logger.debug(f"  消息 {i}: role={msg.get('role')}, content={msg.get('content', '')[:100]}...")
            if msg.get('role') == 'assistant' and 'tool_calls' in msg:
                logger.debug(f"    tool_calls: {msg['tool_calls']}")
            elif msg.get('role') == 'tool':
                logger.debug(f"    tool_call_id: {msg.get('tool_call_id')}, name: {msg.get('name')}")
        
        model_decision = await qwen_llm_service.get_model_decision(
            messages=messages,
            tool_schemas=tool_schemas
        )
        
        if not model_decision:
            logger.error("会话 '%s': 大模型决策失败", session_id)
            raise HTTPException(status_code=500, detail="与大模型通信失败。")
        
        # 3. 根据决策分发任务
        if model_decision.tool_calls:
            logger.info(
                "会话 '%s': 大模型决定调用工具: %s",
                session_id,
                [tc.function.name for tc in model_decision.tool_calls]
            )
            final_answer, messages_to_save = await _handle_tool_calls(
                session_id=session_id,
                model_message=model_decision,
                messages_for_llm=messages,
                current_user_message={"role": "user", "content": request.query},
                db=db
            )
        else:
            logger.info("会话 '%s': 大模型提供了直接回答", session_id)
            final_answer, messages_to_save = _handle_direct_answer(
                model_message=model_decision,
                current_user_message={"role": "user", "content": request.query},
                db=db
            )
        
        # 4. 保存交互历史到数据库
        logger.debug(f"准备保存 {len(messages_to_save)} 条消息到数据库会话 '{session_id}'")
        await save_to_memory(session_id, messages_to_save, db)
        
        # 5. 返回最终结果
        tools_called = []
        if model_decision.tool_calls:
            for tc in model_decision.tool_calls:
                tools_called.append({
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments) if tc.function.arguments else {}
                })
        
        logger.info(
            "会话 '%s': LLM工具调用成功完成",
            session_id,
            extra={
                "request_id": request_id,
                "session_id": session_id,
                "response_length": len(final_answer),
                "tools_called": len(tools_called)
            }
        )
        
        return LLMWithToolsResponse(
            success=True,
            response=final_answer,
            session_id=session_id,
            model_used=settings.llm.model_name or "qwen-max",
            usage={},
            tools_called=tools_called
        )
            
    except Exception as e:
        logger.exception(
            "处理会话 '%s' 的请求时发生未知错误",
            session_id,
            extra={
                "request_id": request_id,
                "session_id": session_id,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"处理请求时发生内部错误: {str(e)}")


# --- 内部辅助函数 ---


async def _handle_tool_calls(
    session_id: str,
    model_message,
    messages_for_llm: List[Dict[str, Any]],
    current_user_message: Dict[str, Any],
    db: AsyncSession
) -> tuple[str, List[Dict[str, Any]]]:
    """处理模型决定调用工具的逻辑分支。"""
    logger.info(
        "会话 '%s': 正在处理工具调用逻辑",
        session_id
    )
    
    # 手动构建包含工具调用的assistant消息
    assistant_message_with_tool_calls = {
        "role": "assistant",
        "content": model_message.content or "",
        "tool_calls": []
    }
    
    # 正确提取tool_calls信息
    if hasattr(model_message, 'tool_calls') and model_message.tool_calls:
        for tc in model_message.tool_calls:
            tool_call_info = {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            assistant_message_with_tool_calls["tool_calls"].append(tool_call_info)
    
    logger.debug(f"构建的assistant消息: {assistant_message_with_tool_calls}")
    logger.debug(f"Assistant消息是否有tool_calls: {'tool_calls' in assistant_message_with_tool_calls}")
    logger.debug(f"tool_calls内容: {assistant_message_with_tool_calls.get('tool_calls', 'None')}")
    
    tasks = [execute_tool(tc, session_id) for tc in model_message.tool_calls]
    tool_results = await asyncio.gather(*tasks)
    
    # 构建用于总结的消息，确保工具调用链的完整性
    messages_for_summary = []
    
    # 添加系统消息（如果有）
    for msg in messages_for_llm:
        if msg.get("role") == "system":
            messages_for_summary.append(msg)
    
    # 添加当前用户消息
    messages_for_summary.append(current_user_message)
    
    # 添加assistant消息和工具结果
    messages_for_summary.append(assistant_message_with_tool_calls)
    messages_for_summary.extend(tool_results)
    
    logger.info("会话 '%s': 正在根据工具结果生成最终总结", session_id)
    logger.debug("发送给LLM的消息用于总结:")
    for i, msg in enumerate(messages_for_summary):
        logger.debug(f"  消息 {i}: role={msg.get('role')}, content={msg.get('content', '')[:100]}...")
        if msg.get('role') == 'assistant' and 'tool_calls' in msg:
            logger.debug(f"    tool_calls: {msg['tool_calls']}")
        elif msg.get('role') == 'tool':
            logger.debug(f"    tool_call_id: {msg.get('tool_call_id')}, name: {msg.get('name')}")
    
    final_answer = await qwen_llm_service.get_summary_from_tool_results(messages_for_summary)
    
    messages_to_save = [
        current_user_message,
        assistant_message_with_tool_calls,
        *tool_results,
        {"role": "assistant", "content": final_answer},
    ]
    
    logger.info("会话 '%s': 工具调用处理完成", session_id)
    return final_answer, messages_to_save


def _handle_direct_answer(
    model_message,
    current_user_message: Dict[str, Any],
    db: AsyncSession = None
) -> tuple[str, List[Dict[str, Any]]]:
    """处理模型直接回答的逻辑分支。"""
    logger.info("大模型提供了直接回答。")
    final_answer = model_message.content or "抱歉，我无法回答。"
    messages_to_save = [
        current_user_message,
        {"role": "assistant", "content": final_answer},
    ]
    return final_answer, messages_to_save


async def execute_tool(tool_call, session_id: str):
    """安全地执行单个工具。"""
    tool_name = tool_call.function.name
    logger.info("正在为会话 '%s' 执行工具: '%s'", session_id, tool_name)
    
    tool_to_call = tool_registry.get_tool(tool_name)
    if not tool_to_call:
        error_msg = f"错误: 找不到名为 '{tool_name}' 的工具。"
        logger.error(
            "为会话 '%s' 尝试调用一个不存在的工具: '%s'", session_id, tool_name
        )
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": error_msg,
        }
    
    try:
        tool_args_str = tool_call.function.arguments
        tool_args = json.loads(tool_args_str) if tool_args_str else {}
        
        logger.debug(
            "为会话 '%s' 调用工具 '%s' 的参数: %s", session_id, tool_name, tool_args
        )
        
        result = await tool_to_call(**tool_args)
        str_result = str(result)
        
        logger.info("为会话 '%s' 成功执行工具 '%s'，结果长度: %d", session_id, tool_name, len(str_result))
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": str_result,
        }
    except Exception as e:
        logger.exception("为会话 '%s' 执行工具 '%s' 时失败。", session_id, tool_name)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": f"执行失败: {e}",
        }


@router.get("/llm-sessions/{session_id}")
async def get_session_history(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取会话历史记录
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    try:
        messages = await session_service.get_history(session_id, db)
        
        logger.info(
            f"获取会话历史: {session_id}",
            extra={
                "request_id": request_id,
                "session_id": session_id,
                "message_count": len(messages)
            }
        )
        
        return {
            "session_id": session_id,
            "messages": messages,
            "context": {}
        }
    except Exception as e:
        logger.error("获取会话历史失败: %s", str(e))
        raise HTTPException(status_code=500, detail="获取会话历史失败")


@router.delete("/llm-sessions/{session_id}")
async def clear_session_history(
    session_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    清除会话历史记录
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    success = await session_service.clear_session(session_id, db)
    if success:
        logger.info(
            f"清除会话历史: {session_id}",
            extra={
                "request_id": request_id,
                "session_id": session_id
            }
        )
        return {"message": "会话历史已清除"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@router.get("/llm-sessions")
async def list_sessions(
    http_request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    列出所有会话
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    sessions = await session_service.list_sessions(db)
    
    logger.info(
        f"列出会话: {len(sessions)} 个会话",
        extra={
            "request_id": request_id,
            "session_count": len(sessions)
        }
    )
    
    return {
        "sessions": sessions,
        "count": len(sessions)
    }


# 导出路由器
__all__ = ["router"]