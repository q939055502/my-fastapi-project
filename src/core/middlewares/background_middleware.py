"""
后台任务中间件
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.background_tasks import BgTasks


class BackGroundTaskMiddleware(BaseHTTPMiddleware):
    """后台任务中间件"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        BgTasks.init_bg_tasks_obj()
        response = await call_next(request)
        BgTasks.execute_tasks()
        return response
