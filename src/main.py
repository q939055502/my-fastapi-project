"""
FastAPI 应用入口模块

负责创建和配置 FastAPI 应用实例，包含：
- 应用生命周期管理（startup/shutdown 事件）
- 应用创建和路由注册
- 文档访问控制（需要登录）

启动命令：uvicorn src.main:app --reload
"""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.core.exceptions import SettingNotFound

try:
    from src.core.config import settings
except ImportError as e:
    raise SettingNotFound("Can not import settings") from e


def create_app():
    """
    创建并配置 FastAPI 应用实例

    配置项：
    - 标题、描述、版本（来自 settings）
    - API 文档路径（/docs, /redoc, /openapi.json）
    - 中间件（来自 app_setup）
    - 异常处理器（来自 app_setup）
    - 路由注册（来自 app_setup）
    - 启动/关闭事件
    """
    from src.app_setup import (
        make_middlewares,
        register_exceptions,
        register_routers,
    )
    from src.foundation.iam import get_current_username, token_manager
    from src.initializers import run_all_initializers
    from src.core.scheduler import scheduler_manager
    from src.core.storage import close_db

    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
    )

    @app.on_event("startup")
    def startup_event():
        """应用启动时执行的初始化任务"""
        token_manager.connect()
        run_all_initializers()
        scheduler_manager.start()

    @app.on_event("shutdown")
    def shutdown_event():
        """应用关闭时执行的清理任务"""
        token_manager.disconnect()
        scheduler_manager.shutdown()
        close_db()

    @app.get("/docs", include_in_schema=False)
    def custom_swagger_ui_html(
        username: str = Depends(get_current_username),
    ):
        """Swagger UI 文档页面，需要登录才能访问"""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get("/redoc", include_in_schema=False)
    def redoc_html(username: str = Depends(get_current_username)):
        """ReDoc 文档页面，需要登录才能访问"""
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=app.title + " - ReDoc",
        )

    @app.get("/openapi.json", include_in_schema=False)
    def get_open_api_endpoint(
        username: str = Depends(get_current_username),
    ):
        """OpenAPI 规范 JSON，需要登录才能访问"""
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        return openapi_schema

    register_exceptions(app)
    register_routers(app, prefix="/api")
    return app


if __name__ == "__main__":
    """直接运行模块时启动 uvicorn 服务"""
    app = create_app()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


app = None


def get_app():
    """获取或创建全局应用实例（单例模式）"""
    global app
    if app is None:
        app = create_app()
    return app


app = get_app()
