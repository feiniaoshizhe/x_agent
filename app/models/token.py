from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.models.base import BaseModel


class RefreshToken(BaseModel):
    """Refresh token model
    
    Used to manage user refresh tokens, supports:
    - Multi-device login (one token per device)
    - Token revocation
    - Token expiration management
    """
    
    __tablename__ = "refresh_tokens"

    # 关联用户字段
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, comment="用户ID")
    
    # token 信息
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True, comment="Token")
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, comment="过期时间")
    
    # 登录设备信息
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="设备名称")
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="设备类型")  # web, mobile, desktop
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, comment="IP地址")  # IPv6 max length 45 characters
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="User Agent")
    
    # 状态字段
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="是否已撤销")
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="撤销时间")
    
    # 时间戳
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后使用时间")
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        if self.is_revoked:
            return False
        return datetime.now(UTC) < self.expires_at
    
    def revoke(self) -> None:
        """Revoke token"""
        self.is_revoked = True
        self.revoked_at = datetime.now(UTC)


class VerificationCode(BaseModel):
    """Verification code model
    
    Used to manage email verification codes and password reset codes, supports:
    - Verification code expiration management
    - Verification code usage limit
    - Verification code type distinction
    """
    
    __tablename__ = "verification_codes"

    # 关联用户
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, comment="用户ID")
    
    # Verification code 信息
    code: Mapped[str] = mapped_column(String(10), index=True, comment="验证码")
    code_type: Mapped[str] = mapped_column(String(20), index=True, comment="验证码类型")  # email_verification, password_reset
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, comment="过期时间")
    
    # 使用状态
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="是否已使用")
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="使用时间")
    attempts: Mapped[int] = mapped_column(Integer, default=0, comment="尝试次数")
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, comment="最大尝试次数")

    def is_valid(self) -> bool:
        """Check if verification code is valid"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.now(UTC) < self.expires_at
    
    def increment_attempts(self) -> None:
        """Increment attempt count"""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """Mark as used"""
        self.is_used = True
        self.used_at = datetime.now(UTC)
