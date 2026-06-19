"""
用户信息相关 Schema

包含:用户信息, 选择用户相关等
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserInfoSchema(BaseModel):
    uuid: str = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    alias: str | None = Field(None, description="姓名/昵称")
    avatar: str | None = Field(None, description="头像URL")
    gender: int = Field(0, description="性别(0=未知,1=男,2=女)")
    is_active: bool = Field(True, description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    last_login: datetime | None = Field(None, description="最后登录时间")
    last_login_ip: str | None = Field(None, description="最后登录IP")


class SelectUserRequest(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    user_uuid: str = Field(..., description="选择的用户UUID")


class SelectUserResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserInfoSchema = Field(..., description="用户信息")
