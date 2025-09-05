"""
Genesis AI 应用日志配置模块
==========================

本模块提供企业级的日志配置功能，支持：
- JSON格式日志输出
- 多日志文件分离（access.log、app.log、error.log）
- 请求ID追踪
- 性能耗时记录
- 日志轮转和大小限制
"""

import logging
import logging.config
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class RequestIdFilter(logging.Filter):
    """请求ID过滤器，为每条日志添加请求ID"""
    
    def filter(self, record):
        # 如果record中没有request_id，设置为N/A
        if not hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'N/A')
        return True


class DurationFilter(logging.Filter):
    """耗时过滤器，为每条日志添加耗时信息"""
    
    def filter(self, record):
        # 如果record中没有duration，设置为0ms
        if not hasattr(record, 'duration'):
            record.duration = getattr(record, 'duration', {'ms': 0})
        return True


class CustomJSONFormatter(logging.Formatter):
    """自定义JSON日志格式化器"""
    
    def format(self, record):
        # 创建基础日志数据
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': record.getMessage(),
            'name': record.name,
            'levelname': record.levelname,
        }
        
        # 添加请求ID
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        # 添加耗时信息
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        
        # 添加异常信息
        if record.exc_info:
            log_data['exc_info'] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
        max_file_size: 单个日志文件最大大小
        backup_count: 备份文件数量
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
    """
    # 确保日志目录存在
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 创建日志文件路径
    access_log_path = log_path / "access.log"
    app_log_path = log_path / "app.log"
    error_log_path = log_path / "error.log"
    
    # 配置日志格式
    json_formatter = CustomJSONFormatter()
    
    # 基础配置
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id': {
                '()': RequestIdFilter,
            },
            'duration': {
                '()': DurationFilter,
            },
        },
        'formatters': {
            'json': {
                '()': CustomJSONFormatter,
            },
        },
        'handlers': {},
        'loggers': {},
    }
    
    # 控制台处理器
    if enable_console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['request_id', 'duration'],
            'stream': sys.stdout,
        }
    
    # 文件处理器
    if enable_file:
        # Access日志处理器
        config['handlers']['access_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filters': ['request_id', 'duration'],
            'filename': str(access_log_path),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8',
        }
        
        # App日志处理器
        config['handlers']['app_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['request_id', 'duration'],
            'filename': str(app_log_path),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8',
        }
        
        # Error日志处理器
        config['handlers']['error_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'filters': ['request_id', 'duration'],
            'filename': str(error_log_path),
            'maxBytes': max_file_size,
            'backupCount': backup_count,
            'encoding': 'utf-8',
        }
    
    # 配置根logger
    root_handlers = []
    if enable_console:
        root_handlers.append('console')
    if enable_file:
        root_handlers.append('app_file')
    
    if root_handlers:
        config['handlers']['root'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['request_id', 'duration'],
            'handlers': root_handlers,
        }
    
    # 配置具体logger
    loggers_config = {
        '': {  # root logger
            'level': log_level,
            'handlers': ['root'] if enable_console else ['app_file'],
            'propagate': False,
        },
        'genesis': {
            'level': log_level,
            'handlers': ['app_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'genesis.access': {
            'level': 'INFO',
            'handlers': ['access_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'genesis.app': {
            'level': log_level,
            'handlers': ['app_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'genesis.error': {
            'level': 'ERROR',
            'handlers': ['error_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': ['app_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'uvicorn.access': {
            'level': 'INFO',
            'handlers': ['access_file'] if enable_file else ['console'],
            'propagate': False,
        },
        'uvicorn.error': {
            'level': 'ERROR',
            'handlers': ['error_file'] if enable_file else ['console'],
            'propagate': False,
        },
    }
    
    config['loggers'] = loggers_config
    
    # 应用配置
    logging.config.dictConfig(config)
    
    # 创建logger实例
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成", extra={
        'log_level': log_level,
        'log_dir': log_dir,
        'enable_console': enable_console,
        'enable_file': enable_file,
    })
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger实例
    
    Args:
        name: logger名称
        
    Returns:
        Logger实例
    """
    return logging.getLogger(name)


def log_request_info(
    logger: logging.Logger,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    request_id: str = "N/A",
    user_agent: str = "",
    remote_addr: str = ""
):
    """
    记录请求信息
    
    Args:
        logger: logger实例
        method: HTTP方法
        url: 请求URL
        status_code: 响应状态码
        duration_ms: 请求耗时（毫秒）
        request_id: 请求ID
        user_agent: 用户代理
        remote_addr: 远程地址
    """
    logger.info(
        "HTTP请求已处理",
        extra={
            'request_id': request_id,
            'duration': {'ms': duration_ms},
            'http': {
                'method': method,
                'url': url,
                'status_code': status_code,
                'user_agent': user_agent,
                'remote_addr': remote_addr,
            }
        }
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    request_id: str = "N/A",
    context: Optional[Dict[str, Any]] = None
):
    """
    记录错误信息
    
    Args:
        logger: logger实例
        error: 异常对象
        request_id: 请求ID
        context: 上下文信息
    """
    logger.error(
        f"发生错误: {str(error)}",
        extra={
            'request_id': request_id,
            'error': {
                'type': type(error).__name__,
                'message': str(error),
                'context': context or {},
            },
            'exc_info': True,
        }
    )


# 导出函数和类
__all__ = [
    'setup_logging',
    'get_logger',
    'RequestIdFilter',
    'DurationFilter',
    'CustomJSONFormatter',
    'log_request_info',
    'log_error',
]