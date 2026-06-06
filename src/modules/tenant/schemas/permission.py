from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantPermissionBase(BaseModel):
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限编码（唯一，格式：资源:操作）")
    type: str = Field(..., description="权限类型：menu/button/api")
    parent_id: int | None = Field(None, description="父级权限ID")
    sort: int = Field(0, description="排序")


class TenantPermissionCreate(TenantPermissionBase):
    pass


class TenantPermissionUpdate(BaseModel):
    name: str | None = Field(None, description="权限名称")
    code: str | None = Field(None, description="权限编码")
    type: str | None = Field(None, description="权限类型")
    parent_id: int | None = Field(None, description="父级权限ID")
    sort: int | None = Field(None, description="排序")
    remark: str | None = Field(None, description="备注")


class TenantPermissionResponse(TenantPermissionBase):
    id: int = Field(..., description="权限ID")
    tenant_id: int = Field(..., description="租户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    remark: str | None = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)


class TenantPermissionTreeResponse(TenantPermissionResponse):
    children: list["TenantPermissionTreeResponse"] | None = Field(
        default_factory=list, description="子权限列表"
    )
