"""
响应格式模块

定义统一的API响应格式。
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.core.constants import HTTP_BAD_REQUEST, HTTP_OK

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(HTTP_OK, description="状态码")
    msg: str = Field("success", description="响应消息")
    data: T | None = Field(None, description="响应数据")
    detail: Any | None = Field(None, description="详细信息")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="响应时间")


def success(
    data: T | None = None,
    msg: str = "success",
    code: int = HTTP_OK,
    detail: Any | None = None
) -> ApiResponse[T]:
    return ApiResponse(code=code, msg=msg, data=data, detail=detail)


def success_page(
    data: list[T],
    total: int,
    page: int,
    page_size: int,
    msg: str = "success"
) -> ApiResponse[dict]:
    return success(
        data={
            "list": data,
            "total": total,
            "page": page,
            "page_size": page_size
        },
        msg=msg
    )


def fail(
    msg: str,
    code: int = HTTP_BAD_REQUEST,
    detail: Any | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content=ApiResponse(
            code=code,
            msg=msg,
            data=None,
            detail=detail
        ).model_dump(mode='json'),
        media_type="application/json; charset=utf-8"
    )
