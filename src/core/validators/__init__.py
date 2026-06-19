"""
数据验证器模块
提供通用的数据验证工具函数和可复用的 Pydantic 校验Mixin。
使用方式:
1. 纯函数调用(适用于任意场景):
   from src.core.validators import validate_phone, validate_password

2. 继承 Mixin(适用Pydantic Schema):
   from pydantic import BaseModel
   from src.core.validators import ValidatorMixin

   class UserCreate(BaseModel, ValidatorMixin):
       username: str
       password: str
       phone: str | None = None
"""

from .validators import (
    ValidatorMixin,
    validate_email,
    validate_id_card,
    validate_password,
    validate_phone,
    validate_username,
)

__all__ = [
    "ValidatorMixin",
    "validate_phone",
    "validate_email",
    "validate_id_card",
    "validate_username",
    "validate_password",
]
