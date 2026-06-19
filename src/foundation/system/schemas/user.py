from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.core.validators import ValidatorMixin


class UserRoleItem(BaseModel):
    """用户角色项"""
    uuid: UUID = Field(..., description="角色UUID")
    name: str = Field(..., description="角色名称")
    remark: str | None = Field(None, description="角色备注")

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(True, description="是否激活")


class UserCreate(UserBase, ValidatorMixin):
    email: EmailStr | None = Field(None, json_schema_extra={"example": "admin@qq.com"}, description="邮箱(可选)")
    phone: str | None = Field(None, json_schema_extra={"example": "13800138000"}, description="手机号(可选)")
    username: str = Field(
        ...,
        json_schema_extra={"example": "admin"},
        min_length=3,
        max_length=20,
        description="用户名(3-20位字母数字下划线)",
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "Admin123"},
        description="密码(至少6位,包含大小写字母和数字中的两种以上)",
    )
    role_uuids: Annotated[list[UUID] | None, Field(default_factory=list, description="角色UUID列表")]


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(None, description="是否激活")
    role_uuids: Annotated[list[UUID] | None, Field(default_factory=list, description="角色UUID列表")]
    remark: str | None = Field(None, description="备注")


class UpdatePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(
        ...,
        description="新密码(至少6位,包含大小写字母和数字中的两种以上)",
    )

    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        from src.core.validators import validate_password

        return validate_password(v)


class UserResponse(UserBase):
    uuid: UUID = Field(..., description="用户UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    last_login: datetime | None = Field(None, description="最后登录时间")
    roles: Annotated[list[UserRoleItem], Field(default_factory=list, description="角色列表")]

    model_config = ConfigDict(from_attributes=True)


class UserListResponseItem(UserBase):
    uuid: UUID = Field(..., description="用户UUID")
    created_at: datetime | None = Field(None, description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class UpdateMyProfileIn(BaseModel):
    """更新个人信息输入"""
    alias: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, description="头像URL")
    gender: int | None = Field(None, ge=0, le=2, description="性别:0-未知,1-男,2-女")
    remark: str | None = Field(None, max_length=200, description="备注")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alias": "管理员",
                "avatar": "https://example.com/avatar.png",
                "gender": 1,
                "remark": "系统管理员账号"
            }
        }
    )


class UserProfileResponse(BaseModel):
    """用户个人信息输出"""
    uuid: UUID = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    alias: str | None = Field(None, description="昵称")
    avatar: str | None = Field(None, description="头像URL")
    email: EmailStr | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    gender: int = Field(0, ge=0, le=2, description="性别:0-未知,1-男,2-女")
    is_active: bool = Field(True, description="是否激活")
    last_login: datetime | None = Field(None, description="最后登录时间")
    last_login_ip: str | None = Field(None, description="最后登录IP")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    remark: str | None = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)
