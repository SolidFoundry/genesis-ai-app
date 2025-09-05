"""
Genesis AI 应用依赖注入容器
============================

本模块使用 dependency-injector 库创建应用的依赖注入容器，
管理应用所有服务依赖关系，实现控制反转（IoC）和依赖注入（DI）。

容器结构：
- core_providers: 核心服务提供商
- adapters: 适配器层
- business_logic: 业务逻辑层
- infrastructure: 基础设施层
- ai_tools: AI 工具层

使用示例：
    from genesis.core.container import container
    db_engine = container.db_engine()
    llm_provider = container.llm_provider()
"""

from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

from src.genesis.core.settings import settings


class CoreProviders(containers.DeclarativeContainer):
    """核心服务提供商容器"""
    
    # 配置提供者
    config = providers.Configuration()
    config.from_pydantic(settings)
    
    # 数据库管理器提供者
    db_manager = providers.Singleton(
        "genesis.infrastructure.database.manager.DatabaseManager",
        config=config.database,
    )
    
    # 数据库引擎提供者
    db_engine = providers.DelegatedFactory(
        db_manager.provided.engine,
    )
    
    # 数据库会话提供者
    db_session = providers.Factory(
        db_manager.provided.session,
    )
    
    # Redis 客户端提供者
    redis_client = providers.Singleton(
        "genesis.infrastructure.cache.redis_client_factory",
        config=config.cache.redis,
    )
    
    # 消息队列连接提供者
    message_broker = providers.Singleton(
        "genesis.infrastructure.messaging.broker_factory",
        config=config.messaging.rabbitmq,
    )


class Adapters(containers.DeclarativeContainer):
    """适配器层容器"""
    
    # 核心服务
    core = providers.DependenciesContainer()
    
    # HTTP 客户端提供者
    http_client = providers.Singleton(
        "genesis.infrastructure.external_apis.http_client_factory",
        config=config.external_apis,
        logger=core.logger,
    )
    
    # 事件总线提供者
    event_bus = providers.Singleton(
        "genesis.infrastructure.messaging.event_bus_factory",
        broker=core.message_broker,
        logger=core.logger,
    )
    
    # 缓存服务提供者
    cache_service = providers.Singleton(
        "genesis.infrastructure.cache.cache_service_factory",
        redis_client=core.redis_client,
        config=config.cache,
        logger=core.logger,
    )


class BusinessLogic(containers.DeclarativeContainer):
    """业务逻辑层容器"""
    
    # 核心服务
    core = providers.DependenciesContainer()
    
    # 适配器服务
    adapters = providers.DependenciesContainer()
    
    # 仓库提供者
    advertising_repository = providers.Factory(
        "genesis.business_logic.repositories.advertising.AdvertisingRepository",
        session=core.db_session,
        logger=core.logger,
    )
    
    # 领域服务提供者
    advertising_domain_service = providers.Factory(
        "genesis.business_logic.agents.domain.advertising.AdvertisingDomainService",
        repository=advertising_repository,
        cache_service=adapters.cache_service,
        logger=core.logger,
    )
    
    # 编排器提供者
    advertising_orchestrator = providers.Factory(
        "genesis.business_logic.agents.orchestrators.AdvertisingOrchestrator",
        domain_service=advertising_domain_service,
        event_bus=adapters.event_bus,
        logger=core.logger,
    )


class Infrastructure(containers.DeclarativeContainer):
    """基础设施层容器"""
    
    # 核心服务
    core = providers.DependenciesContainer()
    
    # 适配器服务
    adapters = providers.DependenciesContainer()
    
    # 业务逻辑服务
    business_logic = providers.DependenciesContainer()
    
    # LLM 提供商容器
    llm_providers = providers.Container(
        # OpenAI 提供商
        openai = providers.Singleton(
            "genesis.infrastructure.llm.providers.openai_provider.OpenAIProvider",
            config=config.llm.providers.openai,
            http_client=adapters.http_client,
        ),
        
        # Qwen 提供商
        qwen = providers.Singleton(
            "genesis.infrastructure.llm.providers.qwen_provider.QwenProvider",
            config=config.llm.providers.qwen,
            http_client=adapters.http_client,
        ),
    )
    
    # 默认 LLM 提供商 - 根据配置选择
    llm_provider = providers.Selector(
        config.llm.default_provider,
        openai=llm_providers.openai,
        qwen=llm_providers.qwen,
    )
    
    # MCP 客户端提供者
    mcp_clients = providers.Container(
        # Stub MCP 客户端
        stub = providers.Singleton(
            "genesis.infrastructure.mcp_clients.StubMCPClient",
            logger=core.logger,
        ),
    )
    
    # 数据库仓库提供者
    db_repositories = providers.Container(
        advertising = providers.Factory(
            "genesis.infrastructure.database.repositories.AdvertisingRepository",
            session=core.db_session,
            logger=core.logger,
        ),
    )


class AITools(containers.DeclarativeContainer):
    """AI 工具层容器"""
    
    # 核心服务
    core = providers.DependenciesContainer()
    
    # 适配器服务
    adapters = providers.DependenciesContainer()
    
    # 基础服务
    infrastructure = providers.DependenciesContainer()
    
    # 通用工具容器
    common_tools = providers.Container(
        # 日期时间工具
        datetime_tool = providers.Singleton(
            "genesis.ai_tools.packages.common_tools.GetDateTimeTool",
            logger=core.logger,
        ),
    )
    
    # AI 工具注册表
    tool_registry = providers.Singleton(
        "genesis.ai_tools.registry.ToolRegistry",
        tools=providers.List(
            common_tools.datetime_tool,
        ),
        logger=core.logger,
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Genesis AI 应用主容器
    
    这是应用的根容器，包含所有子容器和服务提供者。
    通过这个容器可以访问应用的所有依赖项。
    """
    
    # 核心服务
    core = CoreProviders()
    
    # 适配器层
    adapters = Adapters(
        core=core,
    )
    
    # 业务逻辑层
    business_logic = BusinessLogic(
        core=core,
        adapters=adapters,
    )
    
    # 基础设施层
    infrastructure = Infrastructure(
        core=core,
        adapters=adapters,
        business_logic=business_logic,
    )
    
    # AI 工具层
    ai_tools = AITools(
        core=core,
        adapters=adapters,
        infrastructure=infrastructure,
    )
    
    # FastAPI 应用提供者
    fastapi_app = providers.Singleton(
        "genesis.adapters.fastapi.app_factory",
        container=self,
        config=core.config,
        logger=core.logger,
    )
    
    # MCP 服务器提供者
    mcp_server = providers.Singleton(
        "genesis.adapters.mcp.server_factory",
        container=self,
        config=core.config,
        logger=core.logger,
    )
    
    # 初始化方法
    async def init_resources(self):
        """初始化容器资源"""
        # 初始化数据库管理器
        db_manager = self.core.db_manager()
        await db_manager.initialize()
    
    async def shutdown_resources(self):
        """关闭容器资源"""
        # 关闭数据库管理器
        try:
            db_manager = self.core.db_manager()
            await db_manager.close()
        except Exception:
            # 忽略关闭时的错误
            pass


# 创建全局容器实例
container = ApplicationContainer()


# 依赖注入装饰器
def inject_service(service_name: str):
    """服务依赖注入装饰器"""
    def decorator(func):
        return inject(func)
    return decorator


# 便捷的提供者访问器
def get_provider(provider_path: str):
    """获取指定的提供者"""
    path_parts = provider_path.split('.')
    current = container
    
    for part in path_parts:
        if hasattr(current, part):
            current = getattr(current, part)
        else:
            raise ValueError(f"Provider not found: {provider_path}")
    
    return current


# 导出常用的提供者和装饰器
__all__ = [
    "container",
    "ApplicationContainer",
    "inject_service",
    "get_provider",
    "Provide",
]