from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantDictDataBase(BaseModel):
    dict_type_id: int = Field(..., description="字典类型ID")
    label: str = Field(..., description="字典标签")
    value: str = Field(..., description="字典值")
    css_class: str | None = Field(None, description="样式类")
    status: int = Field(1, description="状态：1启用 0禁用")
    sort: int = Field(0, description="排序")


class TenantDictDataCreate(TenantDictDataBase):
    pass


class TenantDictDataUpdate(BaseModel):
    dict_type_id: int | None = Field(None, description="字典类型ID")
    label: str | None = Field(None, description="字典标签")
    value: str | None = Field(None, description="字典值")
    css_class: str | None = Field(None, description="样式类")
    status: int | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")


class TenantDictDataResponse(TenantDictDataBase):
    id: int = Field(..., description="字典数据ID")
    tenant_id: int = Field(..., description="租户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
