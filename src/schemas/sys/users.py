import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱")
    username: Optional[str] = Field(None, description="用户名")
    is_active: Optional[bool] = Field(True, description="是否激活")


class UserCreate(UserBase):
    email: EmailStr = Field(..., example="admin@qq.com", description="邮箱")
    username: str = Field(
        ...,
        example="admin",
        min_length=3,
        max_length=20,
        description="用户名（3-20位字母数字下划线）",
    )
    password: str = Field(
        ...,
        example="AdminPass123",
        min_length=8,
        description="密码（至少8位，包含字母和数字）",
    )
    role_ids: Optional[List[int]] = Field(default_factory=list, description="角色ID列表")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码长度至少8位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱")
    username: Optional[str] = Field(None, description="用户名")
    is_active: Optional[bool] = Field(None, description="是否激活")
    role_ids: Optional[List[int]] = Field(default_factory=list, description="角色ID列表")
    remark: Optional[str] = Field(None, description="备注")


class UpdatePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(
        ...,
        min_length=8,
        description="新密码（至少8位，包含字母和数字）"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("新密码长度至少8位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("新密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("新密码必须包含数字")
        return v


class UserResponse(UserBase):
    id: int = Field(..., description="用户ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    roles: Optional[List] = Field(default_factory=list, description="角色列表")

    class Config:
        from_attributes = True


class UserListResponseItem(UserBase):
    id: int = Field(..., description="用户ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    class Config:
        from_attributes = True
