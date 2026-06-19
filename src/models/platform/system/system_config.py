from sqlalchemy import Column, String, Text

from src.models.base import BaseModel
from src.models.mixins import (
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
    UUIDModel,
)


class SystemConfig(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin, UUIDModel):
    """平台全局配置模型"""
    __tablename__ = "sys_config"

    name = Column(String(100), nullable=False, comment="配置名称")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="配置编码")
    value = Column(Text, nullable=True, comment="配置值")
    config_type = Column(String(20), default="string", comment="配置类型:string/int/json/boolean")
    group = Column(String(50), nullable=True, index=True, comment="配置分组")

    @property
    def typed_value(self):
        """根据 config_type 返回类型化的值"""
        if self.value is None:
            return None

        config_type = self.config_type or "string"

        if config_type == "int":
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return self.value
        elif config_type == "boolean":
            lower_value = self.value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            return self.value
        elif config_type == "json":
            try:
                import json
                return json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                return self.value
        else:
            return self.value
