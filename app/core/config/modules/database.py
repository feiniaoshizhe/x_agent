from typing import Literal

from pydantic import Field, PositiveInt
from app.core.config.base import EnvBaseSettings

class DatabaseSettings(EnvBaseSettings):
    """database configuration"""
    DB_TYPE: Literal["postgresql", "mysql", "oceanbase", "seekdb", "dm8"] = Field(
        description="Database type to use. OceanBase is MySQL-compatible.",
        default="mysql",
    )

    DB_HOST: str = Field(
        description="Hostname or IP address of the database server.",
        default="localhost",
    )

    DB_PORT: PositiveInt = Field(
        description="Port number for database connection.",
        default=3306,
    )

    DB_USERNAME: str = Field(
        description="Username for database authentication.",
        default="root",
    )

    DB_PASSWORD: str = Field(
        description="Password for database authentication.",
        default="123456",
    )

    DB_DATABASE: str = Field(
        description="Name of the database to connect to.",
        default="xagent",
    )

    DB_CHARSET: str = Field(
        description="Character set for database connection.",
        default="",
    )

    DB_EXTRAS: str = Field(
        description="Additional database connection parameters. Example: 'keepalives_idle=60&keepalives=1'",
        default="",
    )

    # connection pool configuration
    ECHO: bool = Field(
        default=False,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_PRE_PING: bool = Field(
        default=True,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_SIZE: PositiveInt = Field(
        default=6,
        description="Database connection pool size (conservative strategy: suitable for 2-core 2GB server)",
    )
    POOL_MAX_OVERFLOW: PositiveInt = Field(
        default=2,
        description="Database connection pool max overflow (conservative strategy: reduce overflow connections)",
    )

