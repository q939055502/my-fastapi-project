from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantMemberBase(BaseModel):
    user_uuid: UUID | None = Field(None, description="用户UUID")
    role: str = Field("member", description="租户内角色")
    is_owner: bool = Field(False, description="是否为租户创建人")
    is_sub_account: bool = Field(False, description="是否为子账号")
    status: bool = Field(True, description="成员启用/禁用状态")


class TenantMemberCreate(TenantMemberBase):
    user_uuid: UUID = Field(..., description="用户UUID")


class TenantMemberUpdate(BaseModel):
    role: str | None = Field(None, description="租户内角色")


class TenantMemberRoleUpdate(BaseModel):
    role_uuids: list[UUID] = Field(..., description="角色UUID列表")


class TenantMemberResponse(TenantMemberBase):
    uuid: UUID = Field(..., description="成员UUID")
    tenant_uuid: UUID = Field(..., description="租户UUID")
    joined_at: datetime | None = Field(None, description="加入时间")
    join_type: str | None = Field(None, description="加入方式")
    audit_status: int | None = Field(None, description="审核状态")
    user: dict | None = Field(None, description="用户信息")
    roles: list[dict] | None = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)