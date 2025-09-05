"""
MCP服务配置模块
=============

本模块提供MCP服务的配置管理，复用项目的基础设施。
"""

from pathlib import Path
from typing import Optional

from src.genesis.core.settings import settings


class MCPConfig:
    """MCP服务配置类"""
    
    def __init__(self):
        """初始化MCP配置"""
        self.server_config = settings.server.mcp_server
        self.app_config = settings.app
        self.logging_config = settings.logging
        self.monitoring_config = settings.monitoring
        
    @property
    def host(self) -> str:
        """获取主机地址"""
        if isinstance(self.server_config, dict):
            return self.server_config.get('host', '0.0.0.0')
        return self.server_config.host
    
    @property
    def port(self) -> int:
        """获取端口"""
        if isinstance(self.server_config, dict):
            return self.server_config.get('port', 8001)
        return self.server_config.port
    
    @property
    def debug(self) -> bool:
        """获取调试模式"""
        if isinstance(self.server_config, dict):
            return self.server_config.get('debug', True)
        return self.server_config.debug
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        if self.debug:
            return "DEBUG"
        return self.app_config.log_level
    
    @property
    def rate_limit_requests_per_minute(self) -> int:
        """获取限流配置"""
        if isinstance(self.server_config, dict):
            return self.server_config.get('rate_limit_requests_per_minute', 100)
        return self.server_config.rate_limit_requests_per_minute
    
    @property
    def heartbeat_interval_seconds(self) -> int:
        """获取心跳间隔"""
        if isinstance(self.server_config, dict):
            return self.server_config.get('heartbeat_interval_seconds', 3600)
        return self.server_config.heartbeat_interval_seconds
    
    @property
    def service_name(self) -> str:
        """获取服务名称"""
        return f"{self.app_config.name} MCP Server"
    
    @property
    def pid_file_path(self) -> Path:
        """获取PID文件路径"""
        return Path.cwd() / "mcp_server.pid"
    
    @property
    def log_file_path(self) -> Path:
        """获取日志文件路径"""
        return Path.cwd() / "logs" / "mcp_server.log"


# 创建全局配置实例
mcp_config = MCPConfig()