import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from src.common.core.constants import RegexConst


class UserBase(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(True, description="是否激活")


class UserCreate(UserBase):
    email: EmailStr = Field(..., json_schema_extra={"example": "admin@qq.com"}, description="邮箱")
    username: str = Field(
        ...,
        json_schema_extra={"example": "admin"},
        min_length=3,
        max_length=20,
        description="用户名（3-20位字母数字下划线）",
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "Admin123"},
        description="密码（至少6位，包含大小写字母和数字中的两种以上）",
    )
    role_uuids: list[UUID] | None = Field(default_factory=list, description="角色UUID列表")

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


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(None, description="是否激活")
    role_uuids: list[UUID] | None = Field(default_factory=list, description="角色UUID列表")
    remark: str | None = Field(None, description="备注")


class UpdatePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(
        ...,
        description="新密码（至少6位，包含大小写字母和数字中的两种以上）",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("新密码长度不能少于6位")
        has_lower = bool(re.search(r"[a-z]", v))
        has_upper = bool(re.search(r"[A-Z]", v))
        has_digit = bool(re.search(r"[0-9]", v))
        if sum([has_lower or has_upper, has_digit]) < 2:
            raise ValueError("新密码必须包含大小写字母和数字中的两种以上")
        return v


class UserResponse(UserBase):
    uuid: UUID = Field(..., description="用户UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    last_login: datetime | None = Field(None, description="最后登录时间")
    roles: list | None = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)


class UserListResponseItem(UserBase):
    uuid: UUID = Field(..., description="用户UUID")
    created_at: datetime | None = Field(None, description="创建时间")

    model_config = ConfigDict(from_attributes=True)