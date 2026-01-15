"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/15 15:36
Description:
FilePath: mcp_server
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, JSON, Boolean
from app.models.base import BaseModel
from typing import Optional, Dict, Any


class MCPServer(BaseModel):
    __tablename__ = "mcp_servers"
    name: Mapped[str] = mapped_column(unique=True, index=True, max_length=50, description="服务器名称")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, description="描述")

    # 连接配置
    transport: Mapped[str] = mapped_column(String(20), nullable=False, comment="传输类型：sse/streamable_http/stdio")
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="服务器 URL（sse/streamable_http）")
    command: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="命令（stdio）")
    args: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="命令参数数组（stdio）")
    headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="HTTP 请求头")
    timeout: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="HTTP 超时时间（秒）")
    sse_read_timeout: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="SSE 读取超时（秒）")

    # UI 增强字段
    tags :  Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="标签数组")
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="图标（emoji）")

    # 状态字段
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否启用：1=是，0=否")
    disabled_tools: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="禁用的工具名称列表")

    def to_mcp_config(self) -> dict:
        """转换为 MCP 配置格式（用于加载到 MCP_SERVERS 缓存）"""
        config: Dict[str, Any] = {
            "transport": self.transport,
        }
        if self.url:
            config["url"] = self.url
        if self.command:
            config["command"] = self.command
        if self.args:
            config["args"] = self.args
        if self.headers:
            config["headers"] = self.headers
        if self.timeout is not None:
            config["timeout"] = self.timeout
        if self.sse_read_timeout is not None:
            config["sse_read_timeout"] = self.sse_read_timeout
        if self.disabled_tools:
            config["disabled_tools"] = self.disabled_tools
        return config