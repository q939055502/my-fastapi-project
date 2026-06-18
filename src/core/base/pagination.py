from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field, PositiveInt

T = TypeVar("T")


class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="总记录数")
    page: PositiveInt = Field(..., description="当前页码")
    page_size: PositiveInt = Field(..., description="每页大小")
    total_pages: int = Field(..., ge=0, description="总页数")


class PaginationResponse(BaseModel, Generic[T]):
    list: Annotated[list[T], Field(description="数据列表")]
    pagination: PaginationInfo = Field(..., description="分页信息")
