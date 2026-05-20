from typing import Optional
from pydantic import Field
from src.schemas.base import BaseSchema


class SystemConfigUpdate(BaseSchema):
    configs: dict[str, str] = Field(..., description="配置项字典，key 是配置编码，value 是配置值")
