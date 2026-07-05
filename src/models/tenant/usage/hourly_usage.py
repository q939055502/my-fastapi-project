from sqlalchemy import Column, Integer, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import ResourceOrgMixin, ResourceOwnerMixin, TimestampMixin


class HourlyUsage(BaseModel, TimestampMixin, ResourceOwnerMixin, ResourceOrgMixin):
    """
    租户每小时用量明细(仅用于前端图表展示、数据分析)
    不参与核心配额校验，核心校验platform_usage(月度表)
    """
    __tablename__ = "platform_hourly_usage"

    usage_hour = Column(String(13), nullable=False, comment="统计小时:YYYY-MM-DD HH")

    storage_delta = Column(BigInteger, default=0, comment="存储变更新增/ -删除")
    storage_total = Column(BigInteger, default=0, comment="当前累计存储总量(MB)")

    bandwidth_delta = Column(BigInteger, default=0, comment="带宽小时消耗(GB)")
    bandwidth_total = Column(BigInteger, default=0, comment="当月累计带宽总量(GB)")

    user_delta = Column(Integer, default=0, comment="用户数变更量")
    user_total = Column(Integer, default=0, comment="当前累计用户总数")

    org_delta = Column(Integer, default=0, comment="组织数变更量")
    org_total = Column(Integer, default=0, comment="当前累计组织总数")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'usage_hour', name='uq_platform_hourly_usage'),
    )
