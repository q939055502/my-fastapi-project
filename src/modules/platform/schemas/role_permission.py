from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RolePermissionBase(BaseModel):
    role_id: int = Field(..., description="角色ID")
    permission_id: int = Field(..., description="权限ID")
    created_by: int | None = Field(None, description="分配人ID")


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):
    role_id: int | None = Field(None, description="角色ID")
    permission_id: int | None = Field(None, description="权限ID")
    created_by: int | None = Field(None, description="分配人ID")


class RolePermissionResponse(RolePermissionBase):
    id: int = Field(..., description="关联ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
