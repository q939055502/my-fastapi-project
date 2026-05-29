
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

# 系统字段列表 - 这些字段在创建、更新时会被自动过滤
SYSTEM_FIELDS = {"id", "is_deleted", "delete_time", "is_system", "created_at", "updated_at"}


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


class Success(BaseModel):
    """通用成功响应"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Any | None = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class Fail(BaseModel):
    """通用失败响应"""
    code: int = Field(400, description="错误码")
    message: str = Field("失败", description="错误消息")
    detail: Any | None = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

