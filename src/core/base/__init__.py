"""Base Package - 统一导出所有基类
包含- BaseSchema: Schema 基类
- PaginationInfo: 分页信息
- PaginationResponse: 分页响应
- BaseRepository: Repository 基类(位于core.storage)
- CREATE_PROTECTED_FIELDS: 创建时受保护字段
- UPDATE_PROTECTED_FIELDS: 更新时受保护字段
"""
from src.core.base.protected_fields import CREATE_PROTECTED_FIELDS, UPDATE_PROTECTED_FIELDS
from src.core.base.schema_base import (
    BaseSchema,
    PaginationInfo,
    PaginationResponse,
)
from src.core.storage.repository_base import (
    BaseRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)

__all__ = [
    # Schema
    "BaseSchema",
    "PaginationInfo",
    "PaginationResponse",
    # Repository
    "BaseRepository",
    "ModelType",
    "CreateSchemaType",
    "UpdateSchemaType",
    # Protected fields
    "CREATE_PROTECTED_FIELDS",
    "UPDATE_PROTECTED_FIELDS",
]
