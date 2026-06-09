
"""
FastAPI 项目包初始化文件

注意：应用入口已迁移至 src.main
"""
# 导出应用实例，保持向后兼容性
try:
    from src.main import app, create_app, get_app
except ImportError:
    pass

__version__ = "1.0.0"

