import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.core.constants import USERNAME_REGEX


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


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
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class TenantInfoSchema(BaseModel):
    tenant_id: int = Field(..., description="租户ID")
    tenant_name: str = Field(..., description="租户名称")
    tenant_code: str = Field(..., description="租户编码")
    member_id: int = Field(..., description="成员ID")
    role: str = Field(..., description="角色")
    is_default: bool = Field(default=False, description="是否默认租户")


class UserInfoSchema(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")


class LoginStep1Response(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    user: UserInfoSchema = Field(..., description="用户信息")
    tenants: list[TenantInfoSchema] = Field(..., description="租户列表")


class SelectTenantRequest(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    tenant_id: int = Field(..., description="选择的租户ID")


class LoginStep2Response(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


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
