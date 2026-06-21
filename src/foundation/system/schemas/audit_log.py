from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="用户ID")
    username: str | None = Field(None, description="用户名")
    tenant_id: int | None = Field(None, description="租户ID")

    module: str = Field("", description="功能模块")
    summary: str = Field("", description="请求描述")
    method: str = Field("", description="请求方法")
    path: str = Field("", description="请求路径")

    status: int = Field(-1, description="状态码")
    response_time: int = Field(0, description="响应时间(单位ms)")

    ip: str | None = Field(None, description="IP地址")
    location: str | None = Field(None, description="操作地点")
    device: str | None = Field(None, description="设备信息")
    browser: str | None = Field(None, description="浏览器")
    os_name: str | None = Field(None, description="操作系统")

    request_args: dict[str, Any] | None = Field(None, description="请求参数")
    request_body: str | None = Field(None, description="请求体")
    response_body: str | None = Field(None, description="响应内容")
    error_msg: str | None = Field(None, description="错误信息")

    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
