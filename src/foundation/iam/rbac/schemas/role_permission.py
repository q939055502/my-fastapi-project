from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RolePermissionCreate(BaseModel):
    role_uuid: UUID = Field(..., description="角色UUID")
    permission_uuids: Annotated[list[UUID], Field(..., description="权限UUID列表")]


class RolePermissionResponse(BaseModel):
    role_id: int = Field(..., description="角色ID")
    permission_id: int = Field(..., description="权限ID")

    model_config = ConfigDict(from_attributes=True)
