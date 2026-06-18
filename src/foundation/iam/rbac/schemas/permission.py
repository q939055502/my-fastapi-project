from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    name: str = Field(..., description="权限名称")
    resource: str = Field(..., description="资源标识，如user、role等")
    action: str = Field(..., description="操作类型，如create、read、update、delete等")
    type: str = Field(..., description="权限类型，menu/button/api")
    parent_uuid: UUID | None = Field(None, description="上级权限UUID")
    sort: int = Field(0, description="排序")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: str | None = Field(None, description="权限名称")
    resource: str | None = Field(None, description="资源标识")
    action: str | None = Field(None, description="操作类型")
    type: str | None = Field(None, description="权限类型")
    parent_uuid: UUID | None = Field(None, description="上级权限UUID")
    sort: int | None = Field(None, description="排序")
    remark: str | None = Field(None, description="备注")


class PermissionResponse(BaseModel):
    uuid: UUID = Field(..., description="权限UUID")
    name: str = Field(..., description="权限名称")
    resource: str = Field(..., description="资源标识")
    action: str = Field(..., description="操作类型")
    type: str = Field(..., description="权限类型")
    parent_id: int | None = Field(None, description="上级权限ID")
    sort: int = Field(0, description="排序")
    remark: str | None = Field(None, description="备注")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class PermissionTreeResponse(PermissionResponse):
    children: list["PermissionTreeResponse"] | None = Field(
        default_factory=list, description="子权限列表"
    )
