"""
通用异常类

定义项目中常用的通用异常。
"""


class DoesNotExist(Exception):
    """资源不存在异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class SettingNotFound(Exception):
    """设置不存在异常"""
    def __init__(self, key: str = None):
        message = f"Setting '{key}' not found" if key else "Setting not found"
        super().__init__(message)
        self.key = key
        self.message = message
