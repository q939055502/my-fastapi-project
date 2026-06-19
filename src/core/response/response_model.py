"""
响应格式模块

定义统一的API响应格式。
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from src.core.base.schema_base import PaginationInfo, PaginationResponse
from src.core.response.response_msg import RESPONSE_MSG

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应模型(泛型)"""
    code: int = Field(description="业务错误码")
    msg: str = Field(description="响应消息")
    data: T | None = Field(None, description="响应数据")
    detail: Any | None = Field(None, description="详细信息(调试用)")
    request_id: str | None = Field(None, description="请求ID(用于追踪)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="响应时间")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 20000,
                "msg": "操作成功",
                "data": None,
                "detail": None,
                "request_id": "abc-123",
                "timestamp": "2026-06-03T12:00:00Z"
            }
        }
    )


def success(data: T | None = None, msg: str = "操作成功", request_id: str | None = None) -> ApiResponse[T]:
    """返回成功响应"""
    return ApiResponse(
        code=20000,
        msg=msg,
        data=data,
        request_id=request_id
    )


def success_page(
    data: list[T],
    total: int,
    page: int,
    page_size: int,
    msg: str = "操作成功",
    request_id: str | None = None
) -> ApiResponse[PaginationResponse[T]]:
    """返回分页成功响应"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=20000,
        msg=msg,
        data=PaginationResponse(
            list=data,
            pagination=PaginationInfo(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        ),
        request_id=request_id
    )


def error_response(
    code: int,
    msg: str,
    detail: Any | None = None,
    request_id: str | None = None
) -> JSONResponse:
    """返回错误响应(统一使用 ApiResponse Schema)"""
    return JSONResponse(
        status_code=code // 100,
        content=ApiResponse(
            code=code,
            msg=msg,
            data=None,
            detail=detail,
            request_id=request_id
        ).model_dump(mode='json'),
        media_type="application/json; charset=utf-8"
    )


def gen_swagger_response(
    codes: list[int],
    description: str = "业务响应结果",
    example_data: dict | None = None,
    is_pagination: bool = False
) -> dict:
    """
    自动生成 Swagger 响应示例

    :param codes: 业务码列表 [20000, 40401, ...]
    :param description: Swagger 描述
    :param example_data: 自定义示例数据(成功响应时使用)
    :param is_pagination: 是否分页响应
    :return: Swagger 标准响应格式
    """
    examples = {}

    for code in codes:
        msg = RESPONSE_MSG.get(code, "未知错误")
        example_name = msg

        if is_pagination and code == 20000:
            data = {
                "list": example_data or [],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 10
                }
            }
        elif code == 20000:
            data = example_data or None
        else:
            data = None

        resp_data = {
            "code": code,
            "msg": msg,
            "data": data,
            "detail": None,
            "request_id": "abc-123",
            "timestamp": "2026-06-03T00:00:00Z"
        }

        examples[example_name] = {"value": resp_data}

    return {
        "description": description,
        "content": {
            "application/json": {
                "examples": examples
            }
        }
    }
