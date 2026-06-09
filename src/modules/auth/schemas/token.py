"""
JWT令牌相关 Schema

包含：JWT载荷、令牌输出、刷新令牌请求等
"""

from datetime import datetime

from pydantic import BaseModel, Field


class JWTPayload(BaseModel):
    user_id: int
    username: str
    exp: datetime
    token_type: str = "access"


class JWTOut(BaseModel):
    """JWT令牌输出模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenRefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int