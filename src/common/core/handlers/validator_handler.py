"""
验证器处理器模块

包含各种数据验证函数。
"""

import re
from typing import Any

from pydantic import ValidationInfo, field_validator
from src.common.core.constants import RegexConst


def validate_phone(phone: str) -> str:
    """校验手机号格式"""
    if not re.match(RegexConst.PHONE, phone):
        raise ValueError("手机号格式错误")
    return phone


def validate_email(email: str) -> str:
    """校验邮箱格式"""
    if not re.match(RegexConst.EMAIL, email):
        raise ValueError("邮箱格式错误")
    return email


def validate_id_card(id_card: str) -> str:
    """校验身份证号格式"""
    if not re.match(RegexConst.ID_CARD, id_card):
        raise ValueError("身份证号格式错误")
    return id_card


class GlobalValidator:
    """全局通用校验器，可被所有Schema复用"""

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str, info: ValidationInfo) -> str:
        """密码强度校验：至少6位，包含大小写字母和数字中的两种以上"""
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        has_lower = bool(re.search(r"[a-z]", v))
        has_upper = bool(re.search(r"[A-Z]", v))
        has_digit = bool(re.search(r"[0-9]", v))
        if sum([has_lower or has_upper, has_digit]) < 2:
            raise ValueError("密码必须包含大小写字母和数字中的两种以上")
        return v

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any, info: ValidationInfo) -> Any:
        """空字符串转None，全局通用"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
