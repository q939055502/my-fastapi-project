from sqlalchemy import Column, String, Integer, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin
from .associations import role_resource_association


class Resource(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """统一资源表（合并菜单、API、按钮）"""
    __tablename__ = "resource"
    __table_args__ = {'extend_existing': True}
    
    code = Column(String(128), nullable=False, comment="资源编码：user/order")
    name = Column(String(128), nullable=False, comment="资源名称：用户管理")
    tenant_id = Column(Integer, nullable=True, comment="租户ID（null=系统级）")
    type = Column(Integer, nullable=False, comment="1=菜单 2=API 3=按钮")
    parent_id = Column(Integer, ForeignKey("resource.id"), nullable=True, comment="父资源ID")

    api_path = Column(String(255), nullable=True, comment="API路径：api/v1/goods/delete")
    api_method = Column(String(10), nullable=True, comment="请求方法：GET/POST/PUT/DELETE")

    path = Column(String(255), comment="路由路径（仅菜单用）")
    icon = Column(String(64), comment="图标（仅菜单用）")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Integer, default=1, comment="1启用 0禁用")

    scene = Column(String(20), default="admin", nullable=False, comment="场景：admin/app/merchant")
    is_system = Column(Boolean, default=False, nullable=False, comment="系统内置资源，创建后不可修改")

    roles = relationship("Role", secondary=role_resource_association, back_populates="resources")
