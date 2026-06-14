"""
用户信息相关 Schema

包含：用户信息、选择用户相关等
"""

from uuid import UUID

from pydantic import BaseModel, Field


class UserInfoSchema(BaseModel):
    uuid: UUID = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="邮箱")


class SelectUserRequest(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    user_uuid: UUID = Field(..., description="选择的用户UUID")


class SelectUserOut(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserInfoSchema = Field(..., description="用户信息")