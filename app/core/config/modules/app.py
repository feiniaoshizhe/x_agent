"""applicationconfigurationmodule"""

from pydantic import Field
from app.core.config.base import EnvBaseSettings

class AppSettings(EnvBaseSettings):
    """Application metadata configuration"""
    
    APP_NAME: str = Field(
        default="x_agent",
        description="Application name"
    )
    APP_DESCRIPTION: str = Field(
        default="x_agent is a FastAPI application.",
        description="Application description",
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="Application version"
    )

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=False,
    )

    ENV: str = Field(
        description="Deployment environment (e.g., 'production', 'development'), default to production",
        default="production",
    )


