from collections.abc import Callable
from enum import Enum


class InterfaceType(Enum):
    PUBLIC = 'public'
    PLATFORM = 'platform'
    TENANT = 'tenant'
    ALL = 'all'


def interface_type(itype: InterfaceType) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.interface_type = itype
        return func
    return decorator


def login_required(func: Callable) -> Callable:
    func.login_required = True
    return func


def disable_data_permission(func: Callable) -> Callable:
    func.disable_data_permission = True
    return func
