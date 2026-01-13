"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/12 09:30
Description:
FilePath: base
"""
from datetime import datetime, UTC
from typing import Optional

from sqlmodel import SQLModel,Field


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    created_by: int = Field(default=None, description="创建人")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="创建时间")
    updated_by: Optional[int] = Field(default=None, description="更新人")
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC), sa_column_kwargs={"onupdate": datetime.now(UTC)},
        description="更新时间"
    )
    is_deleted: bool = Field(default=False, description="是否删除")
    deleted_at: Optional[datetime] = Field(default=None, description="删除时间")
