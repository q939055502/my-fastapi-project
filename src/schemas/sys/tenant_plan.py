from datetime import datetime
from typing import Optional
from pydantic import Field
from src.schemas.base import BaseSchema


class TenantPlanBase(BaseSchema):
    name: str = Field(..., description="套餐名称")
    code: str = Field(..., description="套餐编码")
    is_auto_approve: int = Field(0, description="是否自动通过：0=否，1=是")
    max_users: Optional[int] = Field(None, description="最大用户数")
    max_depts: Optional[int] = Field(None, description="最大部门数")
    max_storage: Optional[int] = Field(None, description="最大存储空间（MB）")
    max_file_size: Optional[int] = Field(None, description="单文件最大大小（MB）")
    price: Optional[int] = Field(None, description="价格（分）")
    features: Optional[str] = Field(None, description="功能特性描述")
    available_modules: Optional[str] = Field(None, description="可用模块列表")
    status: int = Field(1, description="状态：1启用 0禁用")
    sort: int = Field(0, description="排序")


class TenantPlanCreate(TenantPlanBase):
    pass


class TenantPlanUpdate(BaseSchema):
    name: Optional[str] = Field(None, description="套餐名称")
    code: Optional[str] = Field(None, description="套餐编码")
    is_auto_approve: Optional[int] = Field(None, description="是否自动通过")
    max_users: Optional[int] = Field(None, description="最大用户数")
    max_depts: Optional[int] = Field(None, description="最大部门数")
    max_storage: Optional[int] = Field(None, description="最大存储空间（MB）")
    max_file_size: Optional[int] = Field(None, description="单文件最大大小（MB）")
    price: Optional[int] = Field(None, description="价格（分）")
    features: Optional[str] = Field(None, description="功能特性描述")
    available_modules: Optional[str] = Field(None, description="可用模块列表")
    status: Optional[int] = Field(None, description="状态")
    sort: Optional[int] = Field(None, description="排序")
