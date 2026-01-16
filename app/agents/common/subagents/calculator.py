"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/15 18:31
Description:
FilePath: calculator
"""
from langchain.agents import create_agent
from langchain.tools import tool

# from src import config
from app.agents.common import load_chat_model
from app.agents.common.tools import calculator
from app.core.config import settings




calculator_agent = create_agent(
    model=load_chat_model(
        provider="openai",
        model=settings.llm.OPENAI_API_MODEL,
        base_url=settings.llm.OPENAI_API_BASE,
        api_key=settings.llm.OPENAI_API_KEY,

    ),
    tools=[calculator],
    system_prompt="你可以使用计算器工具，处理各种数学计算任务。最终仅返回计算结果，不需要任何额外的解释。",
)


@tool(name_or_callable="calc_agent_tool", description="进行计算任务，输入是数学表达式或描述，输出计算结果。")
async def calculator_agent_tool(description: str) -> str:
    """
    CalcAgent 工具 - 使用子智能体 CalcAgent 进行计算任务
    """
    response = await calculator_agent.ainvoke({"messages": [("user", description)]})
    return response["messages"][-1].content