from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrgBase(BaseModel):
    name: str = Field(..., description="组织名称")
    remark: str = Field("", description="备注")
    sort: int = Field(0, description="排序")
    parent_uuid: UUID | None = Field(None, description="父组织UUID")


class OrgCreate(OrgBase):
    pass


class OrgUpdate(BaseModel):
    name: str | None = Field(None, description="组织名称")
    remark: str | None = Field(None, description="备注")
    sort: int | None = Field(None, description="排序")
    parent_uuid: UUID | None = Field(None, description="父组织UUID")


class OrgResponse(OrgBase):
    uuid: UUID = Field(..., description="组织UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class OrgTreeResponse(OrgResponse):
    children: list["OrgTreeResponse"] | None = Field(
        default_factory=list, description="子组织列表"
    )
