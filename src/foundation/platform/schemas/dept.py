from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeptBase(BaseModel):
    name: str = Field(..., description="部门名称")
    remark: str = Field("", description="备注")
    sort: int = Field(0, description="排序")
    parent_uuid: UUID | None = Field(None, description="父部门UUID")


class DeptCreate(DeptBase):
    pass


class DeptUpdate(BaseModel):
    name: str | None = Field(None, description="部门名称")
    remark: str | None = Field(None, description="备注")
    sort: int | None = Field(None, description="排序")
    parent_uuid: UUID | None = Field(None, description="父部门UUID")


class DeptResponse(DeptBase):
    uuid: UUID = Field(..., description="部门UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class DeptTreeResponse(DeptResponse):
    children: list["DeptTreeResponse"] | None = Field(
        default_factory=list, description="子部门列表"
    )
