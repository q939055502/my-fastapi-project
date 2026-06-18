from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DictDataBase(BaseModel):
    dict_type_uuid: UUID = Field(..., description="字典类型UUID")
    label: str = Field(..., description="字典标签")
    value: str = Field(..., description="字典值")
    css_class: str | None = Field(None, description="样式类")
    status: bool = Field(True, description="状态")
    sort: int = Field(0, description="排序")


class DictDataCreate(DictDataBase):
    pass


class DictDataUpdate(BaseModel):
    dict_type_uuid: UUID | None = Field(None, description="字典类型UUID")
    label: str | None = Field(None, description="字典标签")
    value: str | None = Field(None, description="字典值")
    css_class: str | None = Field(None, description="样式类")
    status: bool | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")


class DictDataResponse(DictDataBase):
    uuid: UUID = Field(..., description="字典数据UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)