"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/13 17:10
Description:
FilePath: graph
"""
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, SummarizationMiddleware, TodoListMiddleware, dynamic_prompt

from app.agents.common.base import BaseAgent

from .context import DeepContext


class DeepAgent(BaseAgent):
    name = "深度分析智能体"
    description = (
        "具备规划、深度分析和子智能体协作能力的智能体，可以处理复杂的多步骤任务"
    )
    context_schema = DeepContext
    capabilities = [
        "file_upload",
        "todo",
        "files",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = None
        self.checkpointer = None

    @staticmethod
    async def get_tools():
        """返回 Deep Agent 的专用工具"""
        tools = []
        # tavily_search = get_tavily_search()
        tavily_search = None
        if tavily_search:
            tools.append(tavily_search)

        # Assert that search tool is available for DeepAgent
        assert tools, (
            "DeepAgent requires at least one search tool. "
            "Please configure TAVILY_API_KEY environment variable to enable web search."
        )
        return tools

    async def get_graph(self, **kwargs):
        """构建 Deep Agent 的图"""
        if self.graph:
            return self.graph

        # 获取上下文配置
        context = self.context_schema.from_file(module_name=self.module_name)

        model = load_chat_model(context.model)
        sub_model = load_chat_model(context.subagents_model)
        tools = await self.get_tools()

        # Build subagents with search tools
        research_sub_agent = _get_research_sub_agent(tools)

        # 使用 create_deep_agent 创建深度智能体
        graph = create_agent(
            model=model,
            tools=tools,
            system_prompt=context.system_prompt,
            middleware=[
                context_aware_prompt,  # 动态系统提示词
                inject_attachment_context,  # 附件上下文注入
                TodoListMiddleware(),
                FilesystemMiddleware(),
                SubAgentMiddleware(
                    default_model=sub_model,
                    default_tools=tools,
                    subagents=[critique_sub_agent, research_sub_agent],
                    default_middleware=[
                        TodoListMiddleware(),  # 子智能体也有 todo 列表
                        FilesystemMiddleware(),  # 当前的两个文件系统是隔离的
                        SummarizationMiddleware(
                            model=sub_model,
                            trigger=("tokens", 110000),
                            keep=("messages", 10),
                            trim_tokens_to_summarize=None,
                        ),
                        PatchToolCallsMiddleware(),
                    ],
                    general_purpose_agent=True,
                ),
                SummarizationMiddleware(
                    model=model,
                    trigger=("tokens", 110000),
                    keep=("messages", 10),
                    trim_tokens_to_summarize=None,
                ),
                PatchToolCallsMiddleware(),
            ],
            checkpointer=await self._get_checkpointer(),
        )

        self.graph = graph
        return graph
