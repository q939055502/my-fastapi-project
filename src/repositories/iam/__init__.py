from .dept_repository import dept_repository
from .permission_repository import permission_repository
from .role_repository import role_repository
from .user_repository import user_repository

__all__ = [
    "user_repository",
    "role_repository",
    "permission_repository",
    "dept_repository",
]
