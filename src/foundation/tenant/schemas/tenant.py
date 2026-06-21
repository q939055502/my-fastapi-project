from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantOwnerUser(BaseModel):
    """租户户主用户信息"""
    uuid: UUID = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="邮箱")

    model_config = ConfigDict(from_attributes=True)


class TenantQuota(BaseModel):
    """租户配额信息"""
    id: int = Field(..., description="配额ID")
    name: str | None = Field(None, description="配额名称")
    code: str | None = Field(None, description="配额编码")

    model_config = ConfigDict(from_attributes=True)


class TenantBase(BaseModel):
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户编码")
    plan_id: int = Field(..., description="套餐ID")
    status: bool = Field(True, description="状态:True启用 False禁用")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")
    company_size: str | None = Field(None, description="公司规模")
    industry: str | None = Field(None, description="行业")
    logo: str | None = Field(None, description="租户Logo")


class TenantCreate(TenantBase):
    owner_user_uuid: UUID = Field(..., description="户主用户UUID")


class TenantUpdate(BaseModel):
    name: str | None = Field(None, description="租户名称")
    code: str | None = Field(None, description="租户编码")
    plan_id: int | None = Field(None, description="套餐ID")
    status: bool | None = Field(None, description="状态")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")
    company_size: str | None = Field(None, description="公司规模")
    industry: str | None = Field(None, description="行业")
    logo: str | None = Field(None, description="租户Logo")


class TenantResponse(TenantBase):
    uuid: UUID = Field(..., description="租户UUID")
    owner_user_uuid: UUID = Field(..., description="户主用户UUID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    expire_date: datetime | None = Field(None, description="到期时间")
    trial_start_date: datetime | None = Field(None, description="试用开始时间")
    trial_end_date: datetime | None = Field(None, description="试用结束时间")
    quota: TenantQuota | None = Field(None, description="配额信息")
    owner_user: TenantOwnerUser | None = Field(None, description="户主用户信息")

    model_config = ConfigDict(from_attributes=True)
