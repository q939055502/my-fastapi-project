"""
接口类型注解模块

提供用于标记接口类型的装饰器,支持:
- 公开接口(无需登录�?- 登录即可访问接口(无需权限�?- 平台级接口(平台管理员专用)
- 租户级接口(租户成员专用�?- 禁用数据权限过滤(特殊场景使用)
"""

from collections.abc import Callable
from enum import Enum


class InterfaceType(Enum):
    PLATFORM = "platform"
    TENANT = "tenant"


def interface_type(itype: InterfaceType):
    def decorator(func: Callable) -> Callable:
        func.interface_type = itype
        return func
    return decorator


def public_api(func: Callable) -> Callable:
    func.is_public = True
    return func


def login_required(func: Callable) -> Callable:
    func.login_required = True
    return func


def disable_data_permission(func: Callable) -> Callable:
    func.disable_data_permission = True
    return func
