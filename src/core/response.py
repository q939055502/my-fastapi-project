
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime
from fastapi.responses import JSONResponse

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """通用分页响应"""
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")


class SuccessResponse(BaseModel, Generic[T]):
    """通用成功响应"""
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ErrorResponse(BaseModel):
    """通用错误响应"""
    code: int = Field(..., description="错误码")
    msg: str = Field(..., description="错误消息")
    detail: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ResponseCode:
    """状态码常量"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


def success(
    data: Optional[T] = None,
    msg: str = "success",
    code: int = ResponseCode.SUCCESS
) -> SuccessResponse[T]:
    return SuccessResponse(code=code, msg=msg, data=data)


def success_page(
    data: List[T],
    total: int,
    page: int,
    page_size: int,
    msg: str = "success"
) -> SuccessResponse[PageResponse[T]]:
    return success(
        data=PageResponse(data=data, total=total, page=page, page_size=page_size),
        msg=msg
    )


def fail(
    msg: str,
    code: int = ResponseCode.BAD_REQUEST,
    detail: Optional[Any] = None
) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content=ErrorResponse(code=code, msg=msg, detail=detail).model_dump(),
        media_type="application/json; charset=utf-8"
    )

