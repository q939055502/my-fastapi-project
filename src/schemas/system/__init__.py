"""
System 系统级 Schema

包含：平台字典类型、平台字典数据、系统配置等 Schema
"""

from .dict_data import DictDataCreate, DictDataResponse, DictDataUpdate
from .dict_type import DictTypeCreate, DictTypeResponse, DictTypeUpdate
from .system_config import SystemConfigUpdate

__all__ = [
    # DictType
    "DictTypeCreate",
    "DictTypeUpdate",
    "DictTypeResponse",
    # DictData
    "DictDataCreate",
    "DictDataUpdate",
    "DictDataResponse",
    # SystemConfig
    "SystemConfigUpdate",
]
