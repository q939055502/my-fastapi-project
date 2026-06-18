"""
用户注册相关 Schema

包含：注册请求、注册响应等
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.core.validators import ValidatorMixin


class UserRegisterSchema(BaseModel, ValidatorMixin):
    username: str = Field(
        ...,
        json_schema_extra={"example": "newuser"},
        min_length=3,
        max_length=20,
        description="用户名（3-20位字母数字下划线）",
    )
    email: EmailStr | None = Field(None, json_schema_extra={"example": "newuser@qq.com"}, description="邮箱（可选）")
    phone: str | None = Field(None, json_schema_extra={"example": "13800138000"}, description="手机号（可选）")
    password: str = Field(
        ...,
        json_schema_extra={"example": "NewPass123"},
        max_length=25,
        description="密码（6-25位，包含大小写字母和数字中的两种以上）",
    )


class UserRegisterOut(BaseModel):
    uuid: str = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)
