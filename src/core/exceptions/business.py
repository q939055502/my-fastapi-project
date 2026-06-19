"""
业务异常类

定义与业务逻辑相关的异常。
"""


class BusinessException(Exception):
    def __init__(
        self,
        code: int,
        detail: str | None = None,
        msg: str | None = None,
    ):
        self.code = code
        self.detail = detail
        self.msg = msg
