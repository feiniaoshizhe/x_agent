"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/15 18:04
Description:

 Define the state structures for the agent

FilePath: state
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class BaseState(BaseModel):
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = Field(default_factory=list)