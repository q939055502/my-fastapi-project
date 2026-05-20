
import re
from typing import Any
from pydantic import field_validator, ValidationInfo
from src.core.constants import PHONE_REGEX, EMAIL_REGEX, ID_CARD_REGEX


def validate_phone(phone: str) -> str:
    """校验手机号格式"""
    if not re.match(PHONE_REGEX, phone):
        raise ValueError("手机号格式错误")
    return phone


def validate_email(email: str) -> str:
    """校验邮箱格式"""
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("邮箱格式错误")
    return email


def validate_id_card(id_card: str) -> str:
    """校验身份证号格式"""
    if not re.match(ID_CARD_REGEX, id_card):
        raise ValueError("身份证号格式错误")
    return id_card


class GlobalValidator:
    """全局通用校验器，可被所有Schema复用"""
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str, info: ValidationInfo) -> str:
        """密码强度校验：至少8位，包含大小写字母和数字"""
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")
        if not re.search(r"[a-z]", v) or not re.search(r"[A-Z]", v) or not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含大小写字母和数字")
        return v

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any, info: ValidationInfo) -> Any:
        """空字符串转None，全局通用"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

