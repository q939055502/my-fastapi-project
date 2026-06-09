from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantPlanBase(BaseModel):
    name: str = Field(..., description="套餐名称")
    code: str = Field(..., description="套餐编码")
    is_auto_approve: int = Field(0, description="是否自动通过：0=否，1=是")
    max_users: int | None = Field(None, description="最大用户数")
    max_depts: int | None = Field(None, description="最大部门数")
    max_storage: int | None = Field(None, description="最大存储空间（MB）")
    max_file_size: int | None = Field(None, description="单文件最大大小（MB）")
    price: int | None = Field(None, description="价格（分）")
    features: str | None = Field(None, description="功能特性描述")
    available_modules: str | None = Field(None, description="可用模块列表")
    status: int = Field(1, description="状态：1启用 0禁用")
    sort: int = Field(0, description="排序")


class TenantPlanCreate(TenantPlanBase):
    pass


class TenantPlanUpdate(BaseModel):
    name: str | None = Field(None, description="套餐名称")
    code: str | None = Field(None, description="套餐编码")
    is_auto_approve: int | None = Field(None, description="是否自动通过")
    max_users: int | None = Field(None, description="最大用户数")
    max_depts: int | None = Field(None, description="最大部门数")
    max_storage: int | None = Field(None, description="最大存储空间（MB）")
    max_file_size: int | None = Field(None, description="单文件最大大小（MB）")
    price: int | None = Field(None, description="价格（分）")
    features: str | None = Field(None, description="功能特性描述")
    available_modules: str | None = Field(None, description="可用模块列表")
    status: int | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")


class TenantPlanResponse(TenantPlanBase):
    id: int = Field(..., description="套餐ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)