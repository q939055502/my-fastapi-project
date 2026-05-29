from datetime import datetime

from pydantic import BaseModel, Field


class BaseRole(BaseModel):
    id: int
    name: str = Field(..., description="角色/职位名称")
    remark: str = ""
    users: list | None = []
    resources: list | None = []
    created_at: datetime | None
    updated_at: datetime | None


class RoleCreate(BaseModel):
    name: str = Field(..., example="管理员", description="角色/职位名称")
    remark: str = Field("", example="管理员角色", description="备注")


class RoleUpdate(BaseModel):
    name: str = Field(..., example="管理员", description="角色/职位名称")
    remark: str = Field("", example="管理员角色", description="备注")
    resource_ids: list[int] = []
