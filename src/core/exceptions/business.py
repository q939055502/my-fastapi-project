"""
业务异常类

定义与业务逻辑相关的异常。
"""

from src.core.enums.response_code import ResponseCode


class BusinessException(Exception):
    def __init__(self, code: ResponseCode, detail: str | None = None):
        self.code = code
        self.detail = detail
