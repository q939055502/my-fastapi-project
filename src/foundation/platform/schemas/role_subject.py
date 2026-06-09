from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleSubjectBase(BaseModel):
    subject_id: int = Field(..., description="主体ID（用户ID或成员ID）")
    subject_type: int = Field(..., description="主体类型：0=平台用户，1=租户成员")
    role_id: int = Field(..., description="角色ID")
    created_by: int | None = Field(None, description="创建人ID")


class RoleSubjectCreate(RoleSubjectBase):
    pass


class RoleSubjectUpdate(BaseModel):
    subject_id: int | None = Field(None, description="主体ID（用户ID或成员ID）")
    subject_type: int | None = Field(None, description="主体类型：0=平台用户，1=租户成员")
    role_id: int | None = Field(None, description="角色ID")
    created_by: int | None = Field(None, description="创建人ID")


class RoleSubjectResponse(RoleSubjectBase):
    id: int = Field(..., description="关联ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
