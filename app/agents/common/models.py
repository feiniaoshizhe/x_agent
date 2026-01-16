"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/13 17:32
Description:
FilePath: model
"""

import traceback
from typing import Literal,TypeAlias

from langchain.chat_models import BaseChatModel
from pydantic import SecretStr

from app.core.logger import logger_manager

logger = logger_manager.get_logger(__name__)


ProviderType: TypeAlias = Literal["openai", "genai", "dashscope", "deepseek", "zhipuai"]

def load_chat_model(
        provider: ProviderType,
        model: str,
        base_url: str,
        api_key: str,
        **kwargs,
) -> BaseChatModel:
    """

    """
    if provider in ["dashscope", "deepseek"]:
        from langchain_deepseek import ChatDeepSeek

        return ChatDeepSeek(
            model=model,
            api_key=SecretStr(api_key),
            base_url=base_url,
            api_base=base_url,
            stream_usage=True,
            **kwargs,
        )
    elif provider == "genai":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            api_key=SecretStr(api_key),
            api_base=base_url,
            streaming=True,
            **kwargs,
        )


    elif provider == "zhipuai":
        from langchain_community.chat_models import ChatZhipuAI

        return ChatZhipuAI(
            model=model,
            api_key=api_key,
            api_base=base_url,
            streaming=True,
            **kwargs,
        )
    else:
        try:  # 其他模型，默认使用OpenAIBase,
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                api_key=SecretStr(api_key),
                base_url=base_url,
                stream_usage=True,
                **kwargs,
            )
        except Exception as e:
            raise ValueError(
                f"Model provider {provider} load failed, {e} \n {traceback.format_exc()}"
            )