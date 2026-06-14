from typing import Any

from pydantic import BaseModel, model_validator

SYSTEM_FIELDS = {"id", "delete_time", "is_system", "created_at", "updated_at"}


class BaseSchema(BaseModel):
    """基础Schema类，自动过滤系统字段"""

    model_config = {"extra": "forbid"}

    @model_validator(mode="before")
    @classmethod
    def filter_system_fields(cls, data: Any) -> Any:
        """自动过滤系统字段，防止前端传递"""
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k not in SYSTEM_FIELDS}
        return data
