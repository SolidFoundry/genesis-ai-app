"""
Genesis AI 应用数据库连接池管理模块
====================================

本模块提供数据库连接池和会话管理功能，包括：
- 异步数据库引擎管理
- 连接池配置和优化
- 数据库会话工厂
- 事务管理支持

使用 SQLAlchemy 2.0 和 asyncpg 驱动程序。
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine, 
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from src.genesis.core.settings import DatabaseConfig


class Base(DeclarativeBase):
    """
    SQLAlchemy ORM 基类
    
    所有数据表模型都应该继承自这个基类。
    提供统一的表配置和元数据管理。
    """
    pass


class DatabaseManager:
    """
    数据库连接池管理器
    
    负责管理数据库连接池的生命周期，包括：
    - 创建和配置异步数据库引擎
    - 管理连接池参数
    - 提供数据库会话工厂
    - 处理连接池的健康检查
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置对象
        """
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库连接池"""
        if self._initialized:
            return
        
        try:
            # 创建异步数据库引擎
            self._engine = create_async_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                future=True,  # 使用 SQLAlchemy 2.0 风格
            )
            
            # 创建会话工厂
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
            
            # 测试连接
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._initialized = True
            
        except Exception as e:
            raise RuntimeError(f"数据库连接池初始化失败: {e}") from e
    
    async def close(self):
        """关闭数据库连接池"""
        if not self._initialized:
            return
        
        try:
            if self._engine:
                await self._engine.dispose()
                self._engine = None
            
            self._session_factory = None
            self._initialized = False
            
        except Exception as e:
            # 记录错误但不抛出异常，确保应用能正常关闭
            print(f"关闭数据库连接池时发生错误: {e}")
    
    @property
    def engine(self) -> AsyncEngine:
        """获取数据库引擎"""
        if not self._initialized or not self._engine:
            raise RuntimeError("数据库管理器未初始化")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """获取会话工厂"""
        if not self._initialized or not self._session_factory:
            raise RuntimeError("数据库管理器未初始化")
        return self._session_factory
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取数据库会话的上下文管理器
        
        使用示例：
            async with db_manager.session() as session:
                result = await session.execute(query)
        """
        if not self._initialized:
            raise RuntimeError("数据库管理器未初始化")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取事务会话的上下文管理器
        
        使用示例：
            async with db_manager.transaction() as session:
                # 执行数据库操作
                session.add(model)
                # 如果发生异常，会自动回滚
        """
        async with self.session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        if not self._initialized:
            return False
        
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def get_pool_status(self) -> dict:
        """获取连接池状态信息"""
        if not self._initialized or not self._engine:
            return {"status": "not_initialized"}
        
        pool = self._engine.pool
        return {
            "status": "initialized",
            "pool_size": pool.size(),
            "pool_timeout": pool.timeout(),
            "max_overflow": pool._max_overflow,
            "current_overflow": pool._overflow,
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
        }


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


async def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化，请先调用 initialize_db")
    return _db_manager


async def initialize_db(config: DatabaseConfig) -> DatabaseManager:
    """
    初始化全局数据库管理器
    
    Args:
        config: 数据库配置
        
    Returns:
        DatabaseManager: 初始化后的数据库管理器
    """
    global _db_manager
    if _db_manager is not None:
        await _db_manager.close()
    
    _db_manager = DatabaseManager(config)
    await _db_manager.initialize()
    return _db_manager


async def close_db():
    """关闭全局数据库管理器"""
    global _db_manager
    if _db_manager is not None:
        await _db_manager.close()
        _db_manager = None


async def get_db_session() -> AsyncSession:
    """
    获取数据库会话的依赖注入函数
    
    专为 FastAPI 依赖注入设计，可以直接在路由中使用：
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            pass
    """
    db_manager = await get_db_manager()
    session_context = db_manager.session()
    session = await session_context.__aenter__()
    # Store the context manager for cleanup
    if not hasattr(get_db_session, '_session_contexts'):
        get_db_session._session_contexts = {}
    get_db_session._session_contexts[id(session)] = session_context
    return session


@asynccontextmanager
async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    获取事务会话的依赖注入函数
    
    专为需要事务的 FastAPI 路由设计：
        @app.post("/users")
        async def create_user(
            user_data: UserCreate,
            session: AsyncSession = Depends(get_db_transaction)
        ):
            pass
    """
    db_manager = await get_db_manager()
    async with db_manager.transaction() as session:
        yield session


# 导出主要的类和函数
__all__ = [
    "Base",
    "DatabaseManager", 
    "get_db_manager",
    "initialize_db",
    "close_db",
    "get_db_session",
    "get_db_transaction",
]