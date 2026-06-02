import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from src.core.constants import USERNAME_REGEX


class CredentialsSchema(BaseModel):
    username: str = Field(..., description="用户名称", example="admin")
    password: str = Field(..., description="密码", example="请输入正确的测试密码")


class JWTOut(BaseModel):
    access_token: str
    refresh_token: str
    username: str
    token_type: str = "bearer"
    expires_in: int


class JWTPayload(BaseModel):
    user_id: int
    username: str
    exp: datetime
    token_type: str = "access"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenRefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRegisterSchema(BaseModel):
    """用户自主注册请求Schema"""
    username: str = Field(
        ...,
        example="newuser",
        min_length=3,
        max_length=20,
        description="用户名（3-20位字母数字下划线）",
    )
    email: EmailStr = Field(..., example="newuser@qq.com", description="邮箱")
    password: str = Field(
        ...,
        example="NewPass123",
        description="密码（至少6位，包含大小写字母和数字中的两种以上）",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        has_lower = bool(re.search(r"[a-z]", v))
        has_upper = bool(re.search(r"[A-Z]", v))
        has_digit = bool(re.search(r"[0-9]", v))
        if sum([has_lower or has_upper, has_digit]) < 2:
            raise ValueError("密码必须包含大小写字母和数字中的两种以上")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(USERNAME_REGEX, v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserRegisterOut(BaseModel):
    """用户注册响应Schema"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)
