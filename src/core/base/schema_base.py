from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field, model_validator

SYSTEM_FIELDS = {"id", "uuid", "delete_time", "is_system", "created_at", "updated_at"}

T = TypeVar("T")


class BaseSchema(BaseModel):
    """基础Schema类,自动过滤系统字段"""

    model_config = {"extra": "forbid"}

    @model_validator(mode="before")
    @classmethod
    def filter_system_fields(cls, data: Any) -> Any:
        """自动过滤系统字段,防止前端传递"""
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k not in SYSTEM_FIELDS}
        return data


class PaginationInfo(BaseModel):
    """分页信息"""
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, description="每页大小")
    total_pages: int = Field(..., ge=0, description="总页数")


class PaginationResponse(BaseModel, Generic[T]):
    """通用分页响应(泛型)"""
    list: Annotated[list[T], Field(description="数据列表")]
    pagination: PaginationInfo = Field(..., description="分页信息")


__all__ = [
    "BaseSchema",
    "PaginationInfo",
    "PaginationResponse",
]
