"""
HTTP审计日志中间件
"""

import json
import re
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from src.common.core.log import logger
from src.common.core.storage import SessionLocal
from src.models.platform import AuditLog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """HTTP审计日志中间件"""

    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.audit_log_paths = ["/api/v1/auditlog/list"]
        self.max_body_size = 1024 * 1024

    def _parse_user_agent(self, user_agent: str) -> tuple[str, str, str]:
        """简单解析 User-Agent 获取浏览器、设备、系统信息"""
        browser = "unknown"
        device = "unknown"
        os = "unknown"

        ua_lower = user_agent.lower()

        if "chrome" in ua_lower and "edg" not in ua_lower:
            browser = "Chrome"
        elif "firefox" in ua_lower:
            browser = "Firefox"
        elif "safari" in ua_lower and "chrome" not in ua_lower:
            browser = "Safari"
        elif "edg" in ua_lower:
            browser = "Edge"
        elif "opera" in ua_lower or "opr" in ua_lower:
            browser = "Opera"

        if "iphone" in ua_lower or "ipad" in ua_lower:
            device = "Mobile"
        elif "android" in ua_lower:
            device = "Mobile"
        elif "mobile" in ua_lower:
            device = "Mobile"
        else:
            device = "Desktop"

        if "windows" in ua_lower:
            os = "Windows"
        elif "mac" in ua_lower and "iphone" not in ua_lower and "ipad" not in ua_lower:
            os = "macOS"
        elif "linux" in ua_lower:
            os = "Linux"
        elif "android" in ua_lower:
            os = "Android"
        elif "iphone" in ua_lower or "ipad" in ua_lower:
            os = "iOS"

        return browser, device, os

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

    async def get_request_body(self, request: Request) -> str | None:
        """获取原始请求体"""
        if request.method not in ["POST", "PUT", "PATCH"]:
            return None

        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            return "[Multipart Form Data]"

        try:
            body = await request.body()
            if body:
                try:
                    body_str = body.decode("utf-8")
                    if len(body_str) > 5000:
                        return body_str[:5000] + "...[TRUNCATED]"
                    return body_str
                except UnicodeDecodeError:
                    return "[Binary Data]"
        except Exception:
            pass
        return None

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

        # 从 request.state.auth_context 获取用户信息
        auth_context = getattr(request.state, "auth_context", None)
        if auth_context:
            data["user_id"] = auth_context.user_id or 0
            data["username"] = auth_context.username
            data["tenant_id"] = auth_context.tenant_id
            data["ip"] = auth_context.client_ip
        else:
            data["user_id"] = 0
            data["username"] = ""
            data["tenant_id"] = None
            data["ip"] = request.client.host if request.client else "unknown"

        # 解析 User-Agent
        user_agent = request.headers.get("user-agent", "")
        browser, device, os = self._parse_user_agent(user_agent)
        data["browser"] = browser
        data["device"] = device
        data["os_name"] = os

        # location 暂时留空，后续可以接入 IP 地理位置解析
        data["location"] = None

        return data

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并记录审计日志"""
        start_time: datetime = datetime.now()

        # 先获取请求体（需要在 call_next 之前，因为请求体只能读一次）
        request_body = await self.get_request_body(request)

        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

        error_msg = None
        try:
            response = await call_next(request)
        except Exception as e:
            error_msg = str(e)[:1000]
            raise
        finally:
            end_time: datetime = datetime.now()
            process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)

            if request.method in self.methods:
                excluded = False
                for path in self.exclude_paths:
                    if re.search(path, request.url.path, re.I) is not None:
                        excluded = True
                        break

                if not excluded:
                    # 获取响应（在异常情况下 response 可能不存在）
                    current_response = None
                    if "response" in locals():
                        current_response = response
                    else:
                        # 构造一个默认响应用于日志
                        current_response = Response(
                            content=b"",
                            status_code=500,
                        )

                    data: dict = self.get_request_log(request=request, response=current_response)
                    data["response_time"] = process_time
                    data["request_args"] = getattr(request.state, "request_args", {})
                    data["request_body"] = request_body

                    if error_msg:
                        data["error_msg"] = error_msg
                        data["status"] = 500

                    try:
                        if "response" in locals():
                            response_copy = Response(
                                content=response.body if hasattr(response, "body") else b"",
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type=response.media_type
                            )
                            data["response_body"] = await self.get_response_body(request, response_copy)
                        else:
                            data["response_body"] = None
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
