from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Column

from src.core.config import settings
from src.core.storage import Base


class BaseModel(Base):
    """SQLAlchemy 基础模型类"""
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    def to_dict(self, exclude_fields: list[str] | None = None) -> dict[str, Any]:
        if exclude_fields is None:
            exclude_fields = []

        d = {}
        for column in self.__table__.columns:
            field_name = column.name
            if field_name not in exclude_fields:
                value = getattr(self, field_name)
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                d[field_name] = value

        return d


__all__ = [
    "BaseModel",
]