"""Base Package - 统一导出所有基类

包含：
- BaseSchema: Schema 基类
- BaseRepository: Repository 基类（位于 core.storage）
- PaginationInfo: 分页信息
- PaginationResponse: 分页响应
"""
from src.core.base.schema_base import BaseSchema
from src.core.base.pagination import PaginationInfo, PaginationResponse
from src.core.storage.repository_base import (
    BaseRepository,
    CreateSchemaType,
    ModelType,
    PROTECTED_SYSTEM_FIELDS,
    UpdateSchemaType,
)

__all__ = [
    # Schema
    "BaseSchema",
    # Repository
    "BaseRepository",
    "ModelType",
    "CreateSchemaType",
    "UpdateSchemaType",
    "PROTECTED_SYSTEM_FIELDS",
    # Pagination
    "PaginationInfo",
    "PaginationResponse",
]
