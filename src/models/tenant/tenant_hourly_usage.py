from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, TimestampMixin


# 重点：删除 SoftDeleteMixin！统计流水数据永远不软删除
class TenantHourlyUsage(BaseModel, TimestampMixin):
    """
    租户每小时用量明细（仅用于前端图表展示、数据分析）
    不参与核心配额校验，核心校验走 tenant_usage（月度表）
    """
    __tablename__ = "tenant_hourly_usage"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, comment="租户ID")
    # 格式严格：2025-08-01 14 (表示8月1日14点~15点)
    usage_hour = Column(String(13), nullable=False, comment="统计小时：YYYY-MM-DD HH")

    # ==================== 核心优化：Integer → BigInteger 防止数值溢出 ====================
    # 存储（MB）：存量指标（总占用空间）
    storage_delta = Column(BigInteger, default=0, comment="存储变更量(MB)：+新增 / -删除")
    storage_total = Column(BigInteger, default=0, comment="当前累计存储总量(MB)")

    # 带宽（GB）：增量指标（当月累计消耗）
    bandwidth_delta = Column(BigInteger, default=0, comment="带宽小时消耗(GB)")
    bandwidth_total = Column(BigInteger, default=0, comment="当月累计带宽总量(GB)")

    # 用户/部门：存量指标（总数量）
    user_delta = Column(Integer, default=0, comment="用户数变更量")
    user_total = Column(Integer, default=0, comment="当前累计用户总数")

    dept_delta = Column(Integer, default=0, comment="部门数变更量")
    dept_total = Column(Integer, default=0, comment="当前累计部门总数")

    # 关联租户
    tenant = relationship("Tenant", back_populates="hourly_usages")

    # 唯一约束：1个租户 1个小时 只能有1条记录（防重复统计）
    __table_args__ = (
        UniqueConstraint('tenant_id', 'usage_hour', name='uq_tenant_hourly_usage'),
    )
