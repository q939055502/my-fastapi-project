"""
租户信息相关 Schema

包含：租户信息、选择租户相关等
"""

from pydantic import BaseModel, Field


class TenantInfoSchema(BaseModel):
    tenant_id: int = Field(..., description="租户ID")
    tenant_name: str = Field(..., description="租户名称")
    tenant_code: str = Field(..., description="租户编码")
    member_id: int = Field(..., description="成员ID")
    role: str = Field(..., description="角色")
    is_default: bool = Field(default=False, description="是否默认租户")


class SelectTenantRequest(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    tenant_id: int = Field(..., description="租户ID")
