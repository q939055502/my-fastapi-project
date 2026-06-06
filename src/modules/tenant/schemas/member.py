from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantMemberBase(BaseModel):
    user_id: int | None = Field(None, description="用户ID")
    role: str = Field("member", description="租户内角色")
    is_owner: int = Field(0, description="是否为租户创建人：0=否，1=是")
    is_sub_account: int = Field(0, description="是否为子账号：0=否，1=是")


class TenantMemberCreate(TenantMemberBase):
    user_id: int = Field(..., description="用户ID")


class TenantMemberUpdate(BaseModel):
    role: str | None = Field(None, description="租户内角色")


class TenantMemberRoleUpdate(BaseModel):
    role_ids: list[int] = Field(..., description="角色ID列表")


class TenantMemberResponse(TenantMemberBase):
    id: int = Field(..., description="成员ID")
    tenant_id: int = Field(..., description="租户ID")
    joined_at: datetime | None = Field(None, description="加入时间")
    join_type: str | None = Field(None, description="加入方式")
    audit_status: int | None = Field(None, description="审核状态")
    user: dict | None = Field(None, description="用户信息")
    roles: list[dict] | None = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)
