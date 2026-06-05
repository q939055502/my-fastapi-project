from pydantic import Field

from src.schemas.base import BaseSchema


class SystemConfigUpdate(BaseSchema):
    configs: dict[str, str] = Field(
        ..., description="配置项字典，key 是配置编码，value 是配置值"
    )


class SystemConfigResponse(BaseSchema):
    id: int = Field(..., description="配置ID")
    config_key: str = Field(..., description="配置编码")
    config_value: str = Field(..., description="配置值")
    description: str = Field(..., description="配置描述")
