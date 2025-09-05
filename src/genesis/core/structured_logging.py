"""
结构化日志格式化器模块

提供企业级的 JSON 格式日志输出，包含请求追踪、性能监控等字段。
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogFormatter(logging.Formatter):
    """
    结构化日志格式化器
    
    输出 JSON 格式的日志，包含以下字段：
    - timestamp: ISO 8601 格式的时间戳
    - message: 日志消息
    - name: 日志器名称
    - levelname: 日志级别
    - request_id: 请求ID (如果有)
    - duration: 执行耗时 (如果有)
    - extra: 额外的上下文信息
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True,
        ensure_ascii: bool = False
    ):
        super().__init__(fmt, datefmt, style, validate)
        self.ensure_ascii = ensure_ascii
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON 格式
        """
        # 基础日志字段
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "message": record.getMessage(),
            "name": record.name,
            "levelname": record.levelname,
        }
        
        # 添加请求ID (如果有)
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        # 添加执行耗时 (如果有)
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration
        
        # 添加文件名和行号 (DEBUG级别)
        if record.levelno == logging.DEBUG:
            log_entry["filename"] = record.filename
            log_entry["lineno"] = record.lineno
        
        # 添加异常信息 (如果有)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加堆栈跟踪 (如果有)
        if record.stack_info:
            log_entry["stack_info"] = self.formatStack(record.stack_info)
        
        # 添加额外的字段
        for key, value in record.__dict__.items():
            if key not in {
                'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'msg', 'name', 'pathname', 'process', 'processName',
                'relativeCreated', 'stack_info', 'thread', 'threadName',
                'request_id', 'duration'
            }:
                log_entry[key] = value
        
        # 转换为 JSON 字符串
        try:
            return json.dumps(
                log_entry,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':'),  # 紧凑格式，节省空间
                default=self._json_serializer
            )
        except (TypeError, ValueError) as e:
            # 如果序列化失败，回退到简单格式
            fallback_entry = {
                "timestamp": log_entry["timestamp"],
                "message": f"日志序列化失败: {str(e)}",
                "name": "structured_log_formatter",
                "levelname": "ERROR",
                "original_message": log_entry.get("message", ""),
            }
            return json.dumps(fallback_entry, ensure_ascii=self.ensure_ascii)
    
    def _json_serializer(self, obj: Any) -> Any:
        """
        JSON 序列化器，处理特殊对象类型
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, time.struct_time):
            return time.strftime('%Y-%m-%d %H:%M:%S', obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)


class AccessLogFormatter(StructuredLogFormatter):
    """
    访问日志格式化器
    
    专门用于 HTTP 请求访问日志，包含性能监控信息
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化访问日志记录
        """
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "message": record.getMessage(),
            "name": record.name,
            "levelname": record.levelname,
        }
        
        # 访问日志特有字段
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        else:
            log_entry["request_id"] = "N/A"
        
        # 执行耗时
        if hasattr(record, 'duration'):
            log_entry["duration"] = {"ms": record.duration}
        
        # HTTP 相关字段
        for attr in ['method', 'url', 'status_code', 'user_agent', 'ip_address']:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
        
        # 转换为 JSON 字符串
        try:
            return json.dumps(
                log_entry,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':'),
                default=self._json_serializer
            )
        except (TypeError, ValueError) as e:
            fallback_entry = {
                "timestamp": log_entry["timestamp"],
                "message": f"访问日志序列化失败: {str(e)}",
                "name": "access_log_formatter",
                "levelname": "ERROR",
            }
            return json.dumps(fallback_entry, ensure_ascii=self.ensure_ascii)


# 导出格式化器类
__all__ = ['StructuredLogFormatter', 'AccessLogFormatter']