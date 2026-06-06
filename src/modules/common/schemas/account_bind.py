"""
Account bind related schemas
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class AccountBindCreate(BaseModel):
    """Create account bind request"""
    bind_type: int
    identifier: str
    is_default: bool = False

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v, info):
        bind_type = info.data.get('bind_type')
        if bind_type == 0:
            if not (v.isdigit() and 10 <= len(v) <= 15):
                raise ValueError('Invalid phone number')
        elif bind_type == 1:
            try:
                EmailStr.validate(v)
            except Exception:
                raise ValueError('Invalid email address') from None
        return v


class AccountBindVerify(BaseModel):
    """Verify bind request"""
    bind_id: int
    verification_code: str


class AccountBindSetDefault(BaseModel):
    """Set default bind request"""
    bind_id: int


class AccountBindResponse(BaseModel):
    """Account bind response"""
    id: int
    user_id: int
    bind_type: int
    identifier: str
    is_default: bool
    status: str
    verified_at: datetime | None = None
    source: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, bind_obj):
        return cls(
            id=bind_obj.id,
            user_id=bind_obj.user_id,
            bind_type=bind_obj.bind_type,
            identifier=bind_obj.identifier,
            is_default=bool(bind_obj.is_default),
            status=bind_obj.status,
            verified_at=bind_obj.verified_at,
            source=bind_obj.source,
            created_at=bind_obj.created_at,
            updated_at=bind_obj.updated_at,
        )
