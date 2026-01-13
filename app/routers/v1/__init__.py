"""API v1 router module - aggregates all v1 routers"""

from .auth import router as auth_router
from .users import router as user_router

# Export all routers
__all__ = ['auth_router', 'user_router']

