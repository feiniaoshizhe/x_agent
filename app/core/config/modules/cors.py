from pydantic import Field
from app.core.config.base import EnvBaseSettings

class CORSSettings(EnvBaseSettings):
    """CORS (Cross-Origin Resource Sharing) configuration"""
    
    CORS_ALLOWED_ORIGINS: str = Field(
        default='*',
        description="Allowed CORS origins (comma-separated)",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Generate CORS configuration (app/core/config/modules/cors.py)"
    )
    CORS_ALLOW_METHODS: str = Field(
        default='*',
        description="Allowed HTTP methods (comma-separated)",
    )
    CORS_ALLOW_HEADERS: str = Field(
        default='*',
        description="Allowed HTTP headers (comma-separated)",
    )
    CORS_EXPOSE_HEADERS: str = Field(
        default='*',
        description="Exposed HTTP headers (comma-separated)",
    )

