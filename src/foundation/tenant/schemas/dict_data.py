from datetime import datetimefrom pydantic import BaseModel, ConfigDict, Fieldclass TenantDictDataBase(BaseModel):
    dict_type_id: int = Field(..., description="�ֵ�����ID")
    label: str = Field(..., description="�ֵ��ǩ")
    value: str = Field(..., description="�ֵ�ֵ")
    css_class: str | None = Field(None, description="��ʽ��")
    status: int = Field(1, description="״̬��1���� 0����")
    sort: int = Field(0, description="����")


class TenantDictDataCreate(TenantDictDataBase):
    pass


class TenantDictDataUpdate(BaseModel):
    dict_type_id: int | None = Field(None, description="�ֵ�����ID")
    label: str | None = Field(None, description="�ֵ��ǩ")
    value: str | None = Field(None, description="�ֵ�ֵ")
    css_class: str | None = Field(None, description="��ʽ��")
    status: int | None = Field(None, description="״̬")
    sort: int | None = Field(None, description="����")


class TenantDictDataResponse(TenantDictDataBase):
    id: int = Field(..., description="�ֵ�����ID")
    tenant_id: int = Field(..., description="�⻧ID")
    created_at: datetime | None = Field(None, description="����ʱ��")
    updated_at: datetime | None = Field(None, description="����ʱ��")

    model_config = ConfigDict(from_attributes=True)
