from datetime import datetime
from typing import Optional
from pydantic import Field
from src.schemas.base import BaseSchema


class TenantBase(BaseSchema):
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户编码")
    plan_id: int = Field(..., description="套餐ID")
    owner_user_id: int = Field(..., description="户主用户ID")
    status: str = Field("active", description="状态：active/suspended/trial/expired")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系人电话")
    contact_email: Optional[str] = Field(None, description="联系人邮箱")
    company_size: Optional[str] = Field(None, description="公司规模")
    industry: Optional[str] = Field(None, description="行业")
    trial_start_date: Optional[datetime] = Field(None, description="试用开始时间")
    trial_end_date: Optional[datetime] = Field(None, description="试用结束时间")
    expire_date: Optional[datetime] = Field(None, description="到期时间")
    logo: Optional[str] = Field(None, description="租户Logo")


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseSchema):
    name: Optional[str] = Field(None, description="租户名称")
    code: Optional[str] = Field(None, description="租户编码")
    plan_id: Optional[int] = Field(None, description="套餐ID")
    status: Optional[str] = Field(None, description="状态")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系人电话")
    contact_email: Optional[str] = Field(None, description="联系人邮箱")
    company_size: Optional[str] = Field(None, description="公司规模")
    industry: Optional[str] = Field(None, description="行业")
    trial_start_date: Optional[datetime] = Field(None, description="试用开始时间")
    trial_end_date: Optional[datetime] = Field(None, description="试用结束时间")
    expire_date: Optional[datetime] = Field(None, description="到期时间")
    logo: Optional[str] = Field(None, description="租户Logo")
