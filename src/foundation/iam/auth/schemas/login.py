"""
登录相关 Schema

包含:登录请求, 登录响应等
"""

from typing import Annotated

from pydantic import BaseModel, Field

from .user import UserInfoSchema


class LoginByPasswordStep1Request(BaseModel):
    account: str = Field(..., description="用户名/手机号/邮箱")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserInfoSchema = Field(..., description="用户信息")


class LoginSelectUserResponse(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    users: Annotated[list[UserInfoSchema], Field(..., description="用户列表")]
