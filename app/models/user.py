from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, String, DateTime, Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.models.base import BaseModel
from app.schemas.common_schema import IGenderEnum
from app.utils.datetime_utils import utc_now, coerce_datetime


class User(BaseModel):
    """usermodel - Complete JWT Auth
    
    Contains complete authentication features:
    - EmailValidate
    - Password reset
    - Multi-device login support (via RefreshToken table)
    """
    
    __tablename__ = "users"

    # 基础字段
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    gender: Mapped[Optional[IGenderEnum]] = mapped_column(String(20), default=IGenderEnum.OTHER, index=True, comment="性别")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")

    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="Generate user model (app/models/user.py)")

    # 时间戳
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 登录失败限制相关
    login_failed_count: Mapped[int] = mapped_column(Integer, default=0, comment="登录失败次数")
    last_failed_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后一次登录失败时间")
    login_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="锁定时间")

    def is_login_locked(self):
        """检查用户是否处于登录锁定状态"""
        lock_deadline = coerce_datetime(self.login_locked_until)
        if lock_deadline is None:
            return False
        return utc_now() < lock_deadline

    def get_remaining_lock_time(self):
        """获取剩余锁定时间（秒）"""
        lock_deadline = coerce_datetime(self.login_locked_until)
        if lock_deadline is None:
            return 0
        remaining = int((lock_deadline - utc_now()).total_seconds())
        return max(0, remaining)

    def calculate_lock_duration(self):
        """根据失败次数计算锁定时长（秒）"""
        if self.login_failed_count < 10:
            return 0

        # 从第10次失败开始，等待时间从1秒开始，每次翻倍
        wait_seconds = 2 ** (self.login_failed_count - 10)

        # 最大锁定时间：365天
        max_seconds = 365 * 24 * 60 * 60
        return min(wait_seconds, max_seconds)

    def increment_failed_login(self):
        """增加登录失败次数并设置锁定时间"""
        self.login_failed_count += 1
        self.last_failed_login_at = utc_now()

        lock_duration = self.calculate_lock_duration()
        if lock_duration > 0:
            self.login_locked_until = utc_now() + timedelta(seconds=lock_duration)

    def reset_failed_login(self):
        """重置登录失败相关字段"""
        self.login_failed_count = 0
        self.last_failed_login_at = None
        self.login_locked_until = None

