"""MySQL database connection management generator"""

from collections.abc import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.logger import logger_manager
from app.core.config.settings import settings

db = settings.database

Base = declarative_base()

class MySQLManager:

    def __init__(self):
        self.logger = logger_manager.get_logger(__name__)
        self.async_engine: AsyncEngine | None = None
        self.async_session_maker: async_sessionmaker | None = None
        self.sync_engine: Engine | None = None
        self.sync_session_maker: sessionmaker | None = None

    @staticmethod
    def get_sqlalchemy_url() -> str:
        """Build SQLAlchemy async connection URL"""
        encoded_password = quote_plus(db.DB_PASSWORD)
        if db.DB_TYPE == "mysql":
            return (
                f"mysql+aiomysql://{db.DB_USERNAME}:{encoded_password}"
                f"@{db.DB_HOST}:{db.DB_PORT}/{db.DB_DATABASE}"
            )
        else:
            raise RuntimeError("Invalid database type.")

    @staticmethod
    def get_sync_sqlalchemy_url() -> str:
        """Build SQLAlchemy sync connection URL"""
        encoded_password = quote_plus(db.DB_PASSWORD)
        if db.DB_TYPE == "mysql":
            return (
                f"mysql+pymysql://{db.DB_USERNAME}:{encoded_password}"
                f"@{db.DB_HOST}:{db.DB_PORT}/{db.DB_DATABASE}"
            )
        else:
            raise RuntimeError("Invalid database type.")
    
    async def initialize(self) -> None:
        """Initialize async connection and session (idempotent)"""
        if self.async_engine:
            self.logger.debug("MySQLManager is already initialized.")
            return
        
        try:

            # Initialize async engine
            self.async_engine = create_async_engine(
                self.get_sqlalchemy_url(),
                echo=db.ECHO,
                pool_pre_ping=db.POOL_PRE_PING,
                pool_timeout=db.POOL_TIMEOUT,
                pool_size=db.POOL_SIZE,
                max_overflow=db.POOL_MAX_OVERFLOW,
                # Set MySQL timezone to UTC (session level)
                connect_args={
                    "init_command": "SET SESSION time_zone = '+00:00'",
                },
            )
            
            self.async_session_maker = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Initialize sync engine (for background tasks)
            self.sync_engine = create_engine(
                self.get_sync_sqlalchemy_url(),
                echo=db.ECHO,
                pool_pre_ping=db.POOL_PRE_PING,
                pool_timeout=db.POOL_TIMEOUT,
                pool_size=db.POOL_SIZE,
                max_overflow=db.POOL_MAX_OVERFLOW,
                connect_args={
                    "init_command": "SET SESSION time_zone = '+00:00'",
                },
            )
            
            self.sync_session_maker = sessionmaker(
                self.sync_engine,
                class_=Session,
                expire_on_commit=False,
            )
            
            self.logger.info("✅ MySQL initialized successfully (async + sync).")
        except Exception:
            self.logger.exception("❌ Failed to initialize MySQL.")
            raise
    
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependencies injection use：return async session generate generator"""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session_maker() as session:
            yield session
    
    def get_sync_db(self) -> Session:
        """For background tasks: return sync session"""
        if not self.sync_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.sync_session_maker()
    
    async def test_connection(self) -> bool:
        """test database connection"""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized.")
        
        try:
            async with self.async_session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    raise RuntimeError("❌ MySQL connection test failed.")
                self.logger.info("✅ MySQL connection test passed.")
                return True
        except Exception:
            self.logger.exception("❌ MySQL connection test failed.")
            raise
    
    async def close(self) -> None:
        """Close connection pool and release resources"""
        if self.async_engine:
            try:
                await self.async_engine.dispose()
                self.async_engine = None
                self.async_session_maker = None
                self.logger.info("✅ MySQL async engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose MySQL async engine.")
                raise
        
        if self.sync_engine:
            try:
                self.sync_engine.dispose()
                self.sync_engine = None
                self.sync_session_maker = None
                self.logger.info("✅ MySQL sync engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose MySQL sync engine.")
                raise
    
    async def __aenter__(self) -> "MySQLManager":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


# singleton instance
mysql_manager = MySQLManager()

