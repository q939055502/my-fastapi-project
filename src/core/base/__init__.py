"""Base Package - 统一导出所有基类
包含- BaseSchema: Schema 基类
- PaginationInfo: 分页信息
- PaginationResponse: 分页响应
- BaseRepository: Repository 基类(位于core.storage)
"""
from src.core.base.schema_base import (
    BaseSchema,
    PaginationInfo,
    PaginationResponse,
)
from src.core.storage.repository_base import (
    PROTECTED_SYSTEM_FIELDS,
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
    "PROTECTED_SYSTEM_FIELDS",
]
