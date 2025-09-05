"""
Genesis AI 应用配置管理模块
===========================

本模块是整个应用读取配置的唯一入口，实现配置的优先级加载逻辑：
1. 首先加载 config/default.yaml (默认配置)
2. 然后根据 APP_ENV 环境变量加载对应环境配置
3. 最后从环境变量和 .env 文件加载配置，覆盖之前的值

使用 pydantic-settings 提供类型安全的配置访问。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ServerConfig(BaseSettings):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    access_log: bool = False
    proxy_headers: bool = False


class RestAPIConfig(ServerConfig):
    """REST API 服务器配置"""
    pass


class MCPServerConfig(ServerConfig):
    """MCP 服务器配置"""
    port: int = 8888
    debug: bool = True
    rate_limit_requests_per_minute: int = 100
    heartbeat_interval_seconds: int = 3600


class ServerSettings(BaseSettings):
    """服务器设置"""
    rest_api: RestAPIConfig = Field(default_factory=RestAPIConfig)
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    user: str = "genesis"
    password: str = "genesis_password"
    host: str = "localhost"
    port: int = 5432
    name: str = "genesis_db"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @property
    def url(self) -> str:
        """构建数据库连接URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseSettings):
    """Redis 缓存配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    decode_responses: bool = True
    ssl: bool = False
    ttl: int = 3600


class CacheSettings(BaseSettings):
    """缓存设置"""
    redis: RedisConfig = Field(default_factory=RedisConfig)


class RabbitMQConfig(BaseSettings):
    """RabbitMQ 消息队列配置"""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    ssl: bool = False


class MessagingSettings(BaseSettings):
    """消息队列设置"""
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)


class LLMProviderConfig(BaseSettings):
    """LLM 提供商配置"""
    base_url: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7


class LLMProvidersConfig(BaseSettings):
    """LLM 提供商集合配置"""
    openai: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        base_url="https://api.openai.com/v1",
        model="gpt-4",
        max_tokens=4096,
        temperature=0.7
    ))
    qwen: LLMProviderConfig = Field(default_factory=lambda: LLMProviderConfig(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-max",
        max_tokens=4096,
        temperature=0.7
    ))


class LLMSettings(BaseSettings):
    """LLM 设置"""
    default_provider: str = "openai"
    providers: LLMProvidersConfig = Field(default_factory=LLMProvidersConfig)
    # 新增的LLM API配置
    api_key: Optional[str] = Field(None, json_schema_extra={"env": "LLM__API_KEY"})
    api_base: Optional[str] = Field(None, json_schema_extra={"env": "LLM__API_BASE"})
    model_name: Optional[str] = Field(None, json_schema_extra={"env": "LLM__MODEL_NAME"})
    # 兼容性别名
    qwen_api_key: Optional[str] = Field(None, json_schema_extra={"env": "QWEN_API_KEY"})
    external_api_llm_api_key: Optional[str] = Field(None, json_schema_extra={"env": "EXTERNAL_API_LLM_API_KEY"})
    external_api_llm_base_url: Optional[str] = Field(None, json_schema_extra={"env": "EXTERNAL_API_LLM_BASE_URL"})
    external_api_timeout: Optional[int] = Field(None, json_schema_extra={"env": "EXTERNAL_API_TIMEOUT"})
    external_api_max_retries: Optional[int] = Field(None, json_schema_extra={"env": "EXTERNAL_API_MAX_RETRIES"})
    # 会话记忆配置
    max_history_messages: int = 10
    default_system_prompt: str = (
        "你是一个通用的万能助手，名叫万能。"
        "请友好、专业地回答用户问题。"
        "特别注意：当且仅当遇到任何需要数学计算或处理数值的问题时，"
        "你必须使用且只能使用 'calculate' 工具来获得精确结果，"
        "不要依赖自己的知识进行计算。"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )


class TracingConfig(BaseSettings):
    """链路追踪配置"""
    enabled: bool = True
    service_name: str = "genesis-ai-app"
    sampler_rate: float = 1.0
    exporter: Dict[str, Any] = Field(default_factory=dict)


class MetricsConfig(BaseSettings):
    """指标配置"""
    enabled: bool = True
    prometheus_endpoint: str = "/metrics"
    exporter: Dict[str, Any] = Field(default_factory=dict)


class ObservabilitySettings(BaseSettings):
    """可观测性设置"""
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


class LoggingConfig(BaseSettings):
    """日志配置"""
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Any] = Field(default_factory=dict)
    handlers: Dict[str, Any] = Field(default_factory=dict)
    loggers: Dict[str, Any] = Field(default_factory=dict)


class DependencyInjectionConfig(BaseSettings):
    """依赖注入配置"""
    auto_wire: bool = True
    scan_packages: List[str] = Field(default_factory=lambda: ["src.genesis"])


class AIToolsConfig(BaseSettings):
    """AI 工具配置"""
    enabled: bool = True
    scan_packages: List[str] = Field(default_factory=lambda: ["src.genesis.ai_tools.packages"])


class ExternalAPIsConfig(BaseSettings):
    """外部 API 配置"""
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1


class DevelopmentConfig(BaseSettings):
    """开发环境特定配置"""
    cors: Dict[str, Any] = Field(default_factory=dict)
    docs: Dict[str, Any] = Field(default_factory=dict)
    test_data: Dict[str, Any] = Field(default_factory=dict)
    debug_toolbar: Dict[str, Any] = Field(default_factory=dict)


class SecurityConfig(BaseSettings):
    """安全配置"""
    cors: Dict[str, Any] = Field(default_factory=dict)
    rate_limit: Dict[str, Any] = Field(default_factory=dict)
    api_key: Dict[str, Any] = Field(default_factory=dict)


class PerformanceConfig(BaseSettings):
    """性能配置"""
    cache_all: bool = True
    compression: bool = True
    gzip_min_size: int = 1024


class HealthConfig(BaseSettings):
    """健康检查配置"""
    enabled: bool = True
    endpoint: str = "/health"
    detailed: bool = False


class MonitoringConfig(BaseSettings):
    """监控配置"""
    enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"


class AppSettings(BaseSettings):
    """应用设置"""
    name: str = "Genesis AI App"
    version: str = "1.0.0"
    description: str = "企业级AI应用启动模板"
    log_level: str = "INFO"
    tenant_mode: str = "multi"
    debug: bool = False


class Settings(BaseSettings):
    """
    Genesis AI 应用主配置类
    
    实现配置的优先级加载逻辑：
    1. 加载 config/default.yaml
    2. 根据 APP_ENV 加载环境配置
    3. 从环境变量加载配置
    """
    
    # 应用配置
    app: AppSettings = Field(default_factory=AppSettings)
    
    # 服务器配置
    server: ServerSettings = Field(default_factory=ServerSettings)
    
    # 数据库配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # 缓存配置
    cache: CacheSettings = Field(default_factory=CacheSettings)
    
    # 消息队列配置
    messaging: MessagingSettings = Field(default_factory=MessagingSettings)
    
    # LLM 配置
    llm: LLMSettings = Field(default_factory=LLMSettings)
    
    # 直接LLM配置（优先级更高）
    openai_api_key: Optional[str] = Field(None, json_schema_extra={"env": "OPENAI_API_KEY"})
    openai_api_base: Optional[str] = Field(None, json_schema_extra={"env": "OPENAI_API_BASE"})
    model_name: Optional[str] = Field(None, json_schema_extra={"env": "MODEL_NAME"})
    
    # 可观测性配置
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    
    # 日志配置
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # 依赖注入配置
    dependency_injection: DependencyInjectionConfig = Field(default_factory=DependencyInjectionConfig)
    
    # AI 工具配置
    ai_tools: AIToolsConfig = Field(default_factory=AIToolsConfig)
    
    # 外部 API 配置
    external_apis: ExternalAPIsConfig = Field(default_factory=ExternalAPIsConfig)
    
    # 开发环境配置
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    
    # 生产环境配置
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # 内部配置
    config_dir: Path = Field(default=Path("config"), exclude=True)
    env: str = Field(default="development", exclude=True)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow"
    }
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config_from_files()
    
    def _load_config_from_files(self):
        """从 YAML 文件加载配置"""
        # 获取配置目录
        config_dir = Path(__file__).parent.parent.parent.parent / self.config_dir
        
        # 加载默认配置
        default_config_path = config_dir / "default.yaml"
        if default_config_path.exists():
            with open(default_config_path, "r", encoding="utf-8") as f:
                default_config = yaml.safe_load(f) or {}
                self._update_from_dict(default_config)
        
        # 加载环境特定配置
        env_config_path = config_dir / f"{self.env}.yaml"
        if env_config_path.exists():
            with open(env_config_path, "r", encoding="utf-8") as f:
                env_config = yaml.safe_load(f) or {}
                self._update_from_dict(env_config)
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, BaseSettings):
                    # 如果是嵌套配置对象，递归更新
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if hasattr(current_value, sub_key):
                                # 跳过只读属性（如url属性）
                                if sub_key == 'url':
                                    continue
                                setattr(current_value, sub_key, sub_value)
                else:
                    # 跳过只读属性
                    if key == 'url':
                        continue
                    setattr(self, key, value)
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.env == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.env == "production"
    
    def get_database_url(self) -> str:
        """获取数据库连接 URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        redis_config = self.cache.redis
        if redis_config.password:
            return f"redis://:{redis_config.password}@{redis_config.host}:{redis_config.port}/{redis_config.db}"
        return f"redis://{redis_config.host}:{redis_config.port}/{redis_config.db}"
    
    def get_llm_provider_config(self, provider: str) -> Optional[LLMProviderConfig]:
        """获取指定 LLM 提供商的配置"""
        return getattr(self.llm.providers, provider, None)


# 创建全局设置实例
settings = Settings()


# 为方便使用，导出常用的配置项
def get_settings() -> Settings:
    """获取全局设置实例"""
    return settings


# 导出配置实例供应用各处使用
__all__ = ["settings", "get_settings", "Settings"]