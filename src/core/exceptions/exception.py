from src.core.enums.error_code import ErrorCode


class BusinessException(Exception):
    def __init__(self, code: ErrorCode, detail: str | None = None):
        self.code = code
        self.detail = detail
