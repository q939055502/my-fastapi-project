from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InviteGenerate(BaseModel):
    invite_type: str = Field(..., description="邀请类型：private/public/apply")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_id: int | None = Field(None, description="默认角色ID")
    need_audit: int = Field(0, description="是否需要审批：0否 1是")
    expire_hours: int | None = Field(None, description="过期小时数")


class GeneratePublicInvite(InviteGenerate):
    invite_type: str = Field("public", const=True, description="公开邀请")
    need_audit: int = Field(0, description="是否需要审批：0否 1是")


class ApplyJoin(BaseModel):
    invite_code: str | None = Field(None, description="邀请码（公开链接用）")
    tenant_id: int | None = Field(None, description="租户ID（搜索申请用）")


class AuditJoin(BaseModel):
    apply_status: int = Field(..., description="申请状态：1通过 2拒绝")
    audit_remark: str | None = Field(None, description="审批备注")


class InviteResponse(BaseModel):
    id: int = Field(..., description="邀请ID")
    tenant_id: int = Field(..., description="租户ID")
    invite_type: str = Field(..., description="邀请类型")
    invite_code: str | None = Field(None, description="邀请码")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_id: int | None = Field(None, description="默认角色ID")
    need_audit: int = Field(..., description="是否需要审批")
    status: int = Field(..., description="状态")
    creator_member_id: int | None = Field(None, description="创建者ID")
    expire_time: int | None = Field(None, description="过期时间")
    created_at: datetime | None = Field(None, description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class AuditListResponse(BaseModel):
    id: int = Field(..., description="申请ID")
    tenant_id: int = Field(..., description="租户ID")
    tenant_name: str = Field(..., description="租户名称")
    apply_user_id: int = Field(..., description="申请人ID")
    apply_username: str = Field(..., description="申请人用户名")
    apply_email: str = Field(..., description="申请人邮箱")
    apply_status: int = Field(..., description="申请状态")
    created_at: datetime | None = Field(None, description="申请时间")

    model_config = ConfigDict(from_attributes=True)
