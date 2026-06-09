from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantDictTypeBase(BaseModel):
    name: str = Field(..., description="字典名称")
    code: str = Field(..., description="字典编码")
    status: int = Field(1, description="状态：1启用 0禁用")
    sort: int = Field(0, description="排序")


class TenantDictTypeCreate(TenantDictTypeBase):
    pass


class TenantDictTypeUpdate(BaseModel):
    name: str | None = Field(None, description="字典名称")
    code: str | None = Field(None, description="字典编码")
    status: int | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")


class TenantDictTypeResponse(TenantDictTypeBase):
    id: int = Field(..., description="字典类型ID")
    tenant_id: int = Field(..., description="租户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
