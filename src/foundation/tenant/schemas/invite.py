from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InviteGenerate(BaseModel):
    invite_type: str = Field(..., description="邀请类型:private/public/apply")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_uuid: UUID | None = Field(None, description="默认角色UUID")
    need_audit: bool = Field(False, description="是否需要审核")
    expire_hours: int | None = Field(None, description="过期小时数")


InviteCreate = InviteGenerate


class GeneratePublicInvite(InviteGenerate):
    invite_type: Literal["public"] = Field("public", description="公开邀请")
    need_audit: bool = Field(False, description="是否需要审核")


class ApplyJoin(BaseModel):
    invite_code: str | None = Field(None, description="邀请码(公开链接用)")
    tenant_uuid: UUID | None = Field(None, description="租户UUID(搜索申请用)")


class AuditJoin(BaseModel):
    apply_status: int = Field(..., description="申请状态:1通过 2拒绝")
    audit_remark: str | None = Field(None, description="审批备注")


class InviteResponse(BaseModel):
    uuid: UUID = Field(..., description="邀请UUID")
    tenant_uuid: UUID = Field(..., description="租户UUID")
    invite_type: str = Field(..., description="邀请类型")
    invite_code: str | None = Field(None, description="邀请码")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_uuid: UUID | None = Field(None, description="默认角色UUID")
    need_audit: bool = Field(..., description="是否需要审核")
    status: bool = Field(..., description="启用/禁用状态")
    creator_member_uuid: UUID | None = Field(None, description="创建者UUID")
    expire_time: int | None = Field(None, description="过期时间")
    created_at: datetime | None = Field(None, description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class AuditListResponse(BaseModel):
    uuid: UUID = Field(..., description="申请UUID")
    tenant_uuid: UUID = Field(..., description="租户UUID")
    tenant_name: str = Field(..., description="租户名称")
    apply_user_uuid: UUID = Field(..., description="申请人UUID")
    apply_username: str = Field(..., description="申请人用户名")
    apply_email: str = Field(..., description="申请人邮箱")
    apply_status: int = Field(..., description="申请状态")
    created_at: datetime | None = Field(None, description="申请时间")

    model_config = ConfigDict(from_attributes=True)
