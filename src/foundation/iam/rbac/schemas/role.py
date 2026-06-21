from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    code: str | None = Field(None, description="角色编码(唯一)")


class RoleCreate(RoleBase):
    code: str = Field(..., description="角色编码(唯一)")


class RoleUpdate(BaseModel):
    name: str | None = Field(None, description="角色名称")
    code: str | None = Field(None, description="角色编码")
    remark: str | None = Field(None, description="备注")
    permission_uuids: list[UUID] | None = Field(None, description="权限UUID列表")


class RoleResponse(RoleBase):
    uuid: UUID = Field(..., description="角色UUID")
    code: str = Field(..., description="角色编码")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    is_system: bool = Field(False, description="是否系统内置")

    model_config = ConfigDict(from_attributes=True)


class RoleWithPermissionsResponse(RoleResponse):
    permissions: list[dict] | None = Field(
        default_factory=list, description="权限列表"
    )
