"""
HTTP审计日志中间件
"""

import json
import re
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from src.core.auth import AuthControl
from src.core.log import logger
from src.core.storage import SessionLocal
from src.models.system import AuditLog


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """HTTP审计日志中间件"""

    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.audit_log_paths = ["/api/v1/auditlog/list"]
        self.max_body_size = 1024 * 1024

    async def get_request_args(self, request: Request) -> dict:
        """获取请求参数"""
        args = {}
        for key, value in request.query_params.items():
            args[key] = value

        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")

            if "multipart/form-data" in content_type:
                return args

            try:
                body = await request.json()
                args.update(body)
            except json.JSONDecodeError:
                try:
                    body = await request.form()
                    args.update(body)
                except Exception:
                    pass

        return args

    async def get_response_body(self, request: Request, response: Response) -> Any:
        """获取响应体"""
        if isinstance(response, StreamingResponse):
            return {"message": "[Streaming Response]"}

        if hasattr(response, "body_iterator") and not hasattr(response, "body"):
            return {"message": "[Streaming Response]"}

        body = b""
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return {
                "code": 0,
                "msg": "Response too large to log",
                "data": None,
            }

        try:
            if hasattr(response, "body"):
                body = response.body
            else:
                body_chunks = []
                async for chunk in response.body_iterator:
                    if not isinstance(chunk, bytes):
                        chunk = chunk.encode(response.charset)
                    body_chunks.append(chunk)

                response.body_iterator = iter(body_chunks)
                body = b"".join(body_chunks)
        except Exception:
            return {"message": "[Unable to read response body]"}

        if any(request.url.path.startswith(path) for path in self.audit_log_paths):
            try:
                data = self.lenient_json(body)
                if isinstance(data, dict):
                    data.pop("response_body", None)
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            item.pop("response_body", None)
                return data
            except Exception:
                return None

        return self.lenient_json(body)

    def lenient_json(self, v: Any) -> Any:
        """宽松的JSON解析"""
        if isinstance(v, bytes):
            try:
                v = v.decode("utf-8")
            except UnicodeDecodeError:
                return str(v)

        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return v

        return str(v)

    def get_request_log(self, request: Request, response: Response) -> dict:
        """获取日志记录数据"""
        data: dict = {
            "path": request.url.path,
            "status": response.status_code,
            "method": request.method,
        }
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.path_regex.match(request.url.path)
                and request.method in route.methods
            ):
                data["module"] = ",".join(route.tags)
                data["summary"] = route.summary
        try:
            auth_header = request.headers.get("Authorization", "")
            token = None
            if auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer "):]

            user_obj = None
            if token:
                user_obj = AuthControl.authenticate_token(token, raise_exc=False)
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception as e:
            logger.debug(f"获取用户信息失败: {str(e)}")
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并记录审计日志"""
        start_time: datetime = datetime.now()

        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

        response = await call_next(request)

        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)

        if request.method in self.methods:
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return response
            data: dict = self.get_request_log(request=request, response=response)
            data["response_time"] = process_time

            data["request_args"] = getattr(request.state, "request_args", {})

            try:
                response_copy = Response(
                    content=response.body if hasattr(response, "body") else b"",
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                data["response_body"] = await self.get_response_body(request, response_copy)
            except Exception as e:
                logger.error(
                    f"获取响应体失败: {request.method} {request.url.path} - {str(e)}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                    },
                )
                data["response_body"] = {"message": "[Unable to read response body]"}

            try:
                with SessionLocal() as session:
                    audit_log = AuditLog(**data)
                    session.add(audit_log)
                    session.commit()
            except Exception as e:
                logger.error(
                    f"审计日志保存失败: {request.method} {request.url.path} - {str(e)}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                    },
                )

        return response
