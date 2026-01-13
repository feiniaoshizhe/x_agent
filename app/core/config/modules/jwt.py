"""JWT authenticationconfigurationmodule"""

from typing import Optional
from pydantic import Field, PositiveInt, SecretStr
from app.core.config.base import EnvBaseSettings

class JWTSettings(EnvBaseSettings):
    """JWT authentication configuration"""

    JWT_SECRET_KEY: SecretStr = Field(
        ...,
        repr=False,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_ACCESS_TOKEN_EXPIRATION: PositiveInt = Field(
        default=1800,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_REFRESH_TOKEN_EXPIRATION: PositiveInt = Field(
        default=86400,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_ISSUER: Optional[str] = Field(
        default="x_agent",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_AUDIENCE: Optional[str] = Field(
        default="x_agent_users",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )

