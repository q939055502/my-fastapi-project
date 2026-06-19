"""
数据验证器模块

提供通用的数据验证工具函数和可复用的 Pydantic 校验器。
"""

import re
from typing import Any

from pydantic import ValidationInfo, field_validator

from src.core.constants import RegexConst


def validate_phone(phone: str | None) -> str | None:
    """校验手机号格式

    Args:
        phone: 手机号,可为空

    Returns:
        str | None: 校验通过的手机号或None

    Raises:
        ValueError: 手机号格式错误
    """
    if phone is None or phone.strip() == "":
        return None
    if not re.match(RegexConst.PHONE, phone):
        raise ValueError("手机号格式不正确")
    return phone


def validate_email(email: str) -> str:
    """校验邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        str: 校验通过的邮箱

    Raises:
        ValueError: 邮箱格式错误
    """
    if not re.match(RegexConst.EMAIL, email):
        raise ValueError("邮箱格式错误")
    return email


def validate_id_card(id_card: str) -> str:
    """校验身份证号格式

    Args:
        id_card: 身份证号

    Returns:
        str: 校验通过的身份证号

    Raises:
        ValueError: 身份证号格式错误
    """
    if not re.match(RegexConst.ID_CARD, id_card):
        raise ValueError("身份证号格式错误")
    return id_card


def validate_username(username: str) -> str:
    """校验用户名格式

    Args:
        username: 用户名

    Returns:
        str: 校验通过的用户名

    Raises:
        ValueError: 用户名格式错误
    """
    if not re.match(RegexConst.USERNAME, username):
        raise ValueError("用户名只能包含字母, 数字和下划线")
    return username


def validate_password(password: str, min_len: int = 6, max_len: int = 25) -> str:
    """校验密码强度

    Args:
        password: 密码
        min_len: 最小长度,默认6
        max_len: 最大长度,默认25

    Returns:
        str: 校验通过的密码

    Raises:
        ValueError: 密码格式错误
    """
    if len(password) < min_len:
        raise ValueError(f"密码长度不能少于{min_len}位")
    if len(password) > max_len:
        raise ValueError(f"密码长度不能超过{max_len}位")
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    if sum([has_lower or has_upper, has_digit]) < 2:
        raise ValueError("密码必须包含大小写字母和数字中的两种以上")
    return password


class ValidatorMixin:
    """通用校验器 Mixin,可被所有 Schema 继承复用"""

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str, info: ValidationInfo) -> str:
        """密码强度校验"""
        return validate_password(v)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str, info: ValidationInfo) -> str:
        """账号校验"""
        return validate_username(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None, info: ValidationInfo) -> str | None:
        """手机号校验"""
        return validate_phone(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None, info: ValidationInfo) -> str | None:
        """邮箱校验"""
        if v is None or v.strip() == "":
            return None
        return validate_email(v)

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any, info: ValidationInfo) -> Any:
        """空字符串转None,全局通用"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
