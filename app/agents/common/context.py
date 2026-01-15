"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/13 16:45
Description:
FilePath: context
"""

import os
import uuid
from pathlib import Path
from typing import Annotated, get_args, get_origin, List, Any, Dict

import yaml
from pydantic import BaseModel, Field

from app.core.logger import logger_manager

logger = logger_manager.get_logger(__name__)

SAVE_DIR = "./saves"

class ConfigurableItem(BaseModel):
    """表示一个可配置项的模型"""
    type: str
    name: str
    options: List[Any] = []
    default: Any = None
    description: str = ""
    template_metadata: Dict[str, Any] = Field(default_factory=dict)



class BaseContext(BaseModel):
    """
    定义一个基础 Context 供 各类 graph 继承

    配置优先级:
    1. 运行时配置(RunnableConfig)：最高优先级，直接从函数参数传入
    2. 文件配置(config.private.yaml)：中等优先级，从文件加载
    3. 类默认配置：最低优先级，类中定义的默认值
    """

    def update(self, data: dict):
        """更新配置字段"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    thread_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="用来唯一标识一个对话线程",
        frozen=True,
        json_schema_extra={
            "name": "线程ID"
        }
    )

    user_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="用来唯一标识一个用户",
        frozen=True,
    )

    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="用来描述智能体的角色和行为",
        # metadata={"name": "系统提示词", "description": "用来描述智能体的角色和行为"},
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="",
        description="智能体的驱动模型，建议选择 Agent 能力较强的模型，不建议使用小参数模型。",
    )

    @classmethod
    def from_file(cls, module_name: str, input_context: dict = None) -> "BaseContext":
        """Load configuration from a YAML file. 用于持久化配置"""

        # 从文件加载配置
        context = cls()
        config_file_path = Path(SAVE_DIR) / "agents" / module_name / "config.yaml"
        if module_name is not None and os.path.exists(config_file_path):
            file_config = {}
            try:
                with open(config_file_path, encoding="utf-8") as f:
                    file_config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"加载智能体配置文件出错: {e}")

            context.update(file_config)

        if input_context:
            context.update(input_context)

        return context

    @classmethod
    def save_to_file(cls, config: dict, module_name: str) -> bool:
        """Save configuration to a YAML file 用于持久化配置"""

        configurable_items = cls.get_configurable_items()
        configurable_config = {}
        for k, v in config.items():
            if k in configurable_items:
                configurable_config[k] = v

        try:
            config_file_path = Path(SAVE_DIR) / "agents" / module_name / "config.yaml"
            # 确保目录存在
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            with open(config_file_path, "w", encoding="utf-8") as f:
                yaml.dump(configurable_config, f, indent=2, allow_unicode=True)

            return True
        except Exception as e:
            logger.error(f"保存智能体配置文件出错: {e}")
            return False

    @classmethod
    def get_configurable_items(cls) -> Dict[str, ConfigurableItem]:
        """实现一个可配置的参数列表，在 UI 上配置时使用"""
        configurable_items = {}

        # 获取模型字段信息
        model_fields = cls.model_fields

        for field_name, field_info in model_fields.items():
            # 检查是否为可配置字段
            field_json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}

            # 如果标记为隐藏，则跳过
            if field_json_schema_extra.get("hide", False):
                continue

            # 如果标记为不可配置，则跳过
            if not field_json_schema_extra.get("configurable", True):
                continue

            # 获取字段类型名称
            type_name = cls._get_type_name(field_info.annotation)

            # 提取 Annotated 的元数据
            template_metadata = cls._extract_template_metadata(field_info.annotation)

            # 获取选项
            options = field_json_schema_extra.get("options", [])
            if callable(options):
                options = options()

            # 获取默认值
            default_value = field_info.default
            if default_value is ...:  # 如果是 Required 类型
                default_value = None
            elif callable(getattr(field_info, 'default_factory', None)):
                if field_info.default_factory is not None:
                    default_value = field_info.default_factory()

            configurable_items[field_name] = ConfigurableItem(
                type=type_name,
                name=field_json_schema_extra.get("name", field_name),
                options=options,
                default=default_value,
                description=field_json_schema_extra.get("description", ""),
                template_metadata=template_metadata
            )

        return configurable_items

    @classmethod
    def _get_type_name(cls, field_type) -> str:
        """获取类型名称，处理 Annotated 类型"""
        # 检查是否是 Annotated 类型
        if get_origin(field_type) is not None:
            # 处理泛型类型如 list[str], Annotated[str, {...}]
            origin = get_origin(field_type)
            if hasattr(origin, "__name__"):
                if origin.__name__ == "Annotated":
                    # Annotated 类型，获取真实类型
                    args = get_args(field_type)
                    if args:
                        return cls._get_type_name(args[0])  # 递归处理真实类型
                return origin.__name__
            else:
                return str(origin)
        elif hasattr(field_type, "__name__"):
            return field_type.__name__
        else:
            return str(field_type)

    @classmethod
    def _extract_template_metadata(cls, field_type) -> dict:
        """从 Annotated 类型中提取模板元数据"""
        if get_origin(field_type) is not None:
            origin = get_origin(field_type)
            if hasattr(origin, "__name__") and origin.__name__ == "Annotated":
                args = get_args(field_type)
                if len(args) > 1:
                    # 查找包含 __template_metadata__ 的字典
                    for metadata in args[1:]:
                        if (
                            isinstance(metadata, dict)
                            and "__template_metadata__" in metadata
                        ):
                            return metadata["__template_metadata__"]
        return {}
