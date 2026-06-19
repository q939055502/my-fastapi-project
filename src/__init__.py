"""FastAPI src.main"""

try:
    from src.main import app, create_app, get_app
except ImportError:
    pass

__version__ = "1.0.0"
