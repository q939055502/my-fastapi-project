from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    code: str | None = Field(None, description="角色编码（唯一）")
    remark: str = Field("", description="备注")


class RoleCreate(RoleBase):
    code: str = Field(..., description="角色编码（唯一）")


class RoleUpdate(BaseModel):
    name: str | None = Field(None, description="角色名称")
    code: str | None = Field(None, description="角色编码")
    remark: str | None = Field(None, description="备注")
    permission_ids: list[int] | None = Field(None, description="权限ID列表")


class RoleResponse(RoleBase):
    id: int = Field(..., description="角色ID")
    code: str = Field(..., description="角色编码")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    is_system: int = Field(0, description="是否系统内置：0=否，1=是")

    model_config = ConfigDict(from_attributes=True)


class RoleWithPermissionsResponse(RoleResponse):
    permissions: list[dict] | None = Field(
        default_factory=list, description="权限列表"
    )
