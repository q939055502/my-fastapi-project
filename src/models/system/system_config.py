from sqlalchemy import Column, Integer, String, Text

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class SystemConfig(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """平台全局配置模型"""
    __tablename__ = "system_config"

    name = Column(String(100), nullable=False, comment="配置名称")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="配置编码")
    value = Column(Text, nullable=True, comment="配置值")
    type = Column(String(20), default="string", comment="配置类型：string/int/json/boolean")
    group = Column(String(50), nullable=True, index=True, comment="配置分组")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Integer, default=1, comment="状态（1=启用，0=禁用）")

    @property
    def typed_value(self):
        """获取类型化后的值"""
        if self.type == "int":
            return int(self.value) if self.value else 0
        elif self.type == "boolean":
            return self.value.lower() in ("true", "1", "yes") if self.value else False
        elif self.type == "json":
            import json
            return json.loads(self.value) if self.value else {}
        else:
            return self.value
