"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/15 18:22
Description:
FilePath: tavily
"""
from typing import Optional

from pydantic import Field

from app.core.config.base import EnvBaseSettings


class TavilySettings(EnvBaseSettings):

    TAVILY_API_KEY: Optional[str] = Field(
        default=None,
        description="Tavily API key",
    )
    ENABLE_WEB_SEARCH: bool = Field(
        default=True,
        description="Enable web search",
    )
