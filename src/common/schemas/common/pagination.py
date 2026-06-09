from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


class PaginationResponse(BaseModel, Generic[T]):
    list: Annotated[list[T], Field(description="数据列表")]
    pagination: PaginationInfo = Field(..., description="分页信息")
