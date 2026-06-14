from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DictTypeBase(BaseModel):
    name: str = Field(..., description="字典名称")
    code: str = Field(..., description="字典编码")
    status: bool = Field(True, description="状态")
    sort: int = Field(0, description="排序")


class DictTypeCreate(DictTypeBase):
    pass


class DictTypeUpdate(BaseModel):
    name: str | None = Field(None, description="字典名称")
    code: str | None = Field(None, description="字典编码")
    status: bool | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")


class DictTypeResponse(DictTypeBase):
    uuid: UUID = Field(..., description="字典类型UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class DictTypeTreeResponse(DictTypeResponse):
    children: list["DictTypeTreeResponse"] | None = Field(
        default_factory=list, description="子字典类型列表"
    )