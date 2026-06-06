from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantRoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色编码（唯一）")
    remark: str = Field("", description="备注")


class TenantRoleCreate(TenantRoleBase):
    pass


class TenantRoleUpdate(BaseModel):
    name: str | None = Field(None, description="角色名称")
    code: str | None = Field(None, description="角色编码")
    remark: str | None = Field(None, description="备注")


class TenantRoleResponse(TenantRoleBase):
    id: int = Field(..., description="角色ID")
    tenant_id: int = Field(..., description="租户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    is_system: int = Field(0, description="是否系统内置：0=否，1=是")

    model_config = ConfigDict(from_attributes=True)


class TenantRoleWithPermissionsResponse(TenantRoleResponse):
    permissions: list[dict] | None = Field(
        default_factory=list, description="权限列表"
    )
