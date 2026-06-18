from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleSubjectCreate(BaseModel):
    role_uuid: UUID = Field(..., description="角色UUID")
    subject_type: int = Field(..., description="主体类型（0=用户，1=成员）")
    subject_uuids: list[UUID] = Field(..., description="主体UUID列表")


class RoleSubjectUpdate(BaseModel):
    role_uuid: UUID = Field(..., description="角色UUID")
    subject_type: int = Field(..., description="主体类型（0=用户，1=成员）")
    subject_uuids: list[UUID] = Field(..., description="主体UUID列表")


class RoleSubjectResponse(BaseModel):
    role_id: int = Field(..., description="角色ID")
    subject_id: int = Field(..., description="主体ID")
    subject_type: int = Field(..., description="主体类型（0=用户，1=成员）")

    model_config = ConfigDict(from_attributes=True)
