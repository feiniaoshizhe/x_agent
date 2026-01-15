"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/12 09:30
Description:
FilePath: base
"""
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class BaseModel(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_by: Mapped[int] = mapped_column(description="创建人")
    created_at: Mapped[datetime] = mapped_column(DateTime,default_factory=lambda: datetime.now(UTC), description="创建时间")
    updated_by: Mapped[Optional[int]] = mapped_column(default=None, description="更新人")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime,
        default_factory=lambda: datetime.now(UTC), sa_column_kwargs={"onupdate": datetime.now(UTC)},
        description="更新时间"
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, description="是否删除")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None, description="删除时间")
