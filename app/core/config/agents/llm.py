"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/16 10:25
Description:
FilePath: llm
"""

from typing import Optional

from pydantic import Field

from app.core.config.base import EnvBaseSettings


class LlmSettings(EnvBaseSettings):

    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key",
    )
    OPENAI_API_BASE: Optional[str] = Field(
        default=None,
        description="OpenAI API base",
    )
    OPENAI_API_MODEL: Optional[str] = Field(
        default="gpt-4-0613",
        description="OpenAI API model",
    )