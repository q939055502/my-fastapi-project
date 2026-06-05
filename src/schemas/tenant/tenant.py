from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantBase(BaseModel):
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户编码")
    plan_id: int = Field(..., description="套餐ID")
    status: int = Field(1, description="状态：1启用 0禁用")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")
    company_size: str | None = Field(None, description="公司规模")
    industry: str | None = Field(None, description="行业")
    logo: str | None = Field(None, description="租户Logo")


class TenantCreate(TenantBase):
    owner_user_id: int = Field(..., description="户主用户ID")


class TenantUpdate(BaseModel):
    name: str | None = Field(None, description="租户名称")
    code: str | None = Field(None, description="租户编码")
    plan_id: int | None = Field(None, description="套餐ID")
    status: int | None = Field(None, description="状态")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")
    company_size: str | None = Field(None, description="公司规模")
    industry: str | None = Field(None, description="行业")
    logo: str | None = Field(None, description="租户Logo")


class TenantResponse(TenantBase):
    id: int = Field(..., description="租户ID")
    owner_user_id: int = Field(..., description="户主用户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    expire_date: datetime | None = Field(None, description="到期时间")
    trial_start_date: datetime | None = Field(None, description="试用开始时间")
    trial_end_date: datetime | None = Field(None, description="试用结束时间")

    model_config = ConfigDict(from_attributes=True)
