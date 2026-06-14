from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
    UUIDModel,
)


class Dept(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin, UUIDModel):
    """部门模型"""
    __tablename__ = "iam_dept"

    name = Column(String(50), nullable=False, comment="部门名称")
    code = Column(String(50), nullable=True, comment="部门编码")
    tenant_id = Column(BigInteger, nullable=True, comment="租户ID（null=系统级）")
    parent_id = Column(BigInteger, nullable=True, comment="父部门ID")
    level = Column(Integer, default=0, comment="部门层级")
    path = Column(String(500), nullable=True, comment="部门路径（如：1/2/3/）")
    leader = Column(String(50), nullable=True, comment="部门负责人")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="部门邮箱")

    users = relationship("User", back_populates="dept", foreign_keys="User.dept_id")


class DeptClosure(BaseModel, TimestampMixin, SoftDeleteMixin):
    """部门闭包表（用于高效查询树形结构）"""
    __tablename__ = "iam_dept_closure"

    ancestor = Column(BigInteger, nullable=False, comment="祖先节点")
    descendant = Column(BigInteger, nullable=False, comment="后代节点")
    level = Column(Integer, default=0, comment="层级深度")
