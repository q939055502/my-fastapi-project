from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantBase(BaseModel):
    name: str | None = Field(None, description="租户名称")
    code: str | None = Field(None, description="租户编码")
    plan_id: int | None = Field(None, description="套餐ID")
    status: str | None = Field("active", description="状态")


class TenantCreate(TenantBase):
    name: str = Field(..., example="我的公司", description="租户名称")
    code: str = Field(..., example="my_company", description="租户编码")
    plan_id: int = Field(..., description="套餐ID")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")


class TenantUpdate(BaseModel):
    name: str | None = Field(None, description="租户名称")
    plan_id: int | None = Field(None, description="套餐ID")
    status: str | None = Field(None, description="状态")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")


class TenantResponse(TenantBase):
    id: int = Field(..., description="租户ID")
    owner_user_id: int = Field(..., description="户主用户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class UserTenantRelationResponse(BaseModel):
    tenant_id: int = Field(..., description="租户ID")
    tenant_name: str = Field(..., description="租户名称")
    is_owner: bool = Field(..., description="是否为户主")
    joined_at: datetime | None = Field(None, description="加入时间")

    model_config = ConfigDict(from_attributes=True)


class UserTenantListResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    tenants: list[UserTenantRelationResponse] = Field(default_factory=list, description="关联的租户列表")


class SwitchTenantRequest(BaseModel):
    tenant_id: int = Field(..., description="目标租户ID")


class TenantMemberResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    is_owner: bool = Field(..., description="是否为户主")
    joined_at: datetime | None = Field(None, description="加入时间")
    roles: list[dict] = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)
