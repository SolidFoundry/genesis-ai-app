"""
Genesis AI 应用简化依赖注入容器
============================

本模块提供简化的依赖注入容器，只包含数据库相关功能。
"""

from dependency_injector import containers, providers

from .settings import settings


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


class Application(containers.DeclarativeContainer):
    """应用程序容器"""
    
    # 核心服务
    core = providers.Container(CoreProviders)


# 创建全局容器实例
container = Application()

# 异步初始化方法
async def init_resources():
    """初始化容器资源"""
    pass

async def shutdown_resources():
    """关闭容器资源"""
    pass

# 导出容器实例
__all__ = ["container", "init_resources", "shutdown_resources"]