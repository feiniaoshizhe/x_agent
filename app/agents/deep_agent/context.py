"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/13 17:11
Description:
FilePath: context
"""

from typing import Annotated

from pydantic import Field

from app.agents.common.context import BaseContext
from app.agents.deep_agent.prompts import DEEP_PROMPT

class DeepContext(BaseContext):
    """
    Deep Agent 的上下文配置，继承自 BaseContext
    专门用于深度分析任务的配置管理
    """

    # 深度分析专用的系统提示词
    system_prompt: str = Field(
        default=DEEP_PROMPT,
        description="Deep智能体的角色和行为指导"
        # metadata={"name": "系统提示词", "description": "Deep智能体的角色和行为指导"},
    )
    subagents_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="siliconflow/deepseek-ai/DeepSeek-V3.2",
        description="The model used by sub-agents (e.g., critique-agent, research-agent).",
    )
