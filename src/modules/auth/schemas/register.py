"""
用户注册相关 Schema

包含：注册请求、注册响应等
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.common.core.constants import RegexConst


class UserRegisterSchema(BaseModel):
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
        if not re.match(RegexConst.USERNAME, v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserRegisterOut(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="用户名（3-20位字母数字下划线）",
    )
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        has_lower = bool(re.search(r"[a-z]", v))
        has_upper = bool(re.search(r"[A-Z]", v))
        has_digit = bool(re.search(r"[0-9]", v))
        if sum([has_lower or has_upper, has_digit]) < 2:
            raise ValueError("密码必须包含大小写字母和数字中的两种以上")
        return v