from datetime import datetimefrom pydantic import BaseModel, ConfigDict, Fieldclass TenantDictTypeBase(BaseModel):
    name: str = Field(..., description="�ֵ�����")
    code: str = Field(..., description="�ֵ����")
    status: int = Field(1, description="״̬��1���� 0����")
    sort: int = Field(0, description="����")


class TenantDictTypeCreate(TenantDictTypeBase):
    pass


class TenantDictTypeUpdate(BaseModel):
    name: str | None = Field(None, description="�ֵ�����")
    code: str | None = Field(None, description="�ֵ����")
    status: int | None = Field(None, description="״̬")
    sort: int | None = Field(None, description="����")


class TenantDictTypeResponse(TenantDictTypeBase):
    id: int = Field(..., description="�ֵ�����ID")
    tenant_id: int = Field(..., description="�⻧ID")
    created_at: datetime | None = Field(None, description="����ʱ��")
    updated_at: datetime | None = Field(None, description="����ʱ��")

    model_config = ConfigDict(from_attributes=True)
