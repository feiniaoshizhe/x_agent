"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/12 10:13
Description:
FilePath: lifespan
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import db_manager
from app.core.logger import logger_manager
from app.core.redis import redis_manager

# Create Logger instance
logger = logger_manager.get_logger(__name__)


@asynccontextmanager
# Create lifespan
async def lifespan(_app: FastAPI):
    """Application lifespan management"""
    logger.info("🚩 Starting the application...")
    logger.info(f"🚧 You are working in {os.getenv('ENV', 'development')} environment")

    try:
        # Initialize database connection
        await db_manager.initialize()
        logger.info("🎉 Database connections initialized successfully")
        await db_manager.test_connections()
        logger.info("🎉 Database connections test successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application will start without database connections")

    try:
        # Initialize Redis connection
        await redis_manager.initialize_async()
        logger.info("🎉 Redis connections initialized successfully")
        await redis_manager.async_test_connection()
        logger.info("🎉 Redis connections test successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.warning("⚠️ Application will start without Redis connections")

    yield

    # Close database connection
    try:
        await db_manager.close()
        logger.info("🎉 Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Database connection closed failed: {e}")
        logger.warning("⚠️ Database connection closed failed")

    # Close Redis connections
    try:
        await redis_manager.close()
        logger.info("🎉 Redis connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection closed failed: {e}")
        logger.warning("⚠️ Redis connection closed failed")