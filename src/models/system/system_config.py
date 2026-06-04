from sqlalchemy import Column, String, Text

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
)


class SystemConfig(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, SortMixin):
    """平台全局配置模型"""
    __tablename__ = "system_config"

    name = Column(String(100), nullable=False, comment="配置名称")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="配置编码")
    value = Column(Text, nullable=True, comment="配置值")
    config_type = Column(String(20), default="string", comment="配置类型：string/int/json/boolean")
    group = Column(String(50), nullable=True, index=True, comment="配置分组")

    @property
    def typed_value(self):
        """获取类型化后的值"""
        if self.config_type == "int":
            return int(self.value) if self.value else 0
        elif self.config_type == "boolean":
            return self.value.lower() in ("true", "1", "yes") if self.value else False
        elif self.config_type == "json":
            import json
            return json.loads(self.value) if self.value else {}
        else:
            return self.value
