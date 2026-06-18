import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class UUIDModel:
    """UUID 混合类"""
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=lambda: uuid.uuid4())


class TimestampMixin:
    """时间戳混合类"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """软删除混合类

    仅使用 delete_time 字段判断软删除状态：
    - delete_time 为 None 表示未删除
    - delete_time 有值表示已删除
    """
    delete_time = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    def soft_delete(self):
        """执行软删除"""
        self.delete_time = datetime.now()

    def restore(self):
        """恢复已删除数据"""
        self.delete_time = None

    def is_deleted_status(self) -> bool:
        """判断是否已被软删除"""
        return self.delete_time is not None


class RemarkMixin:
    """备注描述混合类"""
    remark = Column(String(500), nullable=True, comment="备注")


class EnableStatusMixin:
    """启用/禁用状态 Mixin

    适用于需要表示启用/禁用状态的模型
    """
    status = Column(Boolean, default=True, comment="启用/禁用状态")


class TenantStatusMixin:
    """租户状态 Mixin

    适用于租户模型，表示租户的业务状态，使用 TENANT_STATUS_* 常量
    """
    status = Column(String(20), default="active", comment="状态（使用 TENANT_STATUS_* 常量：active/suspended/trial/expired）")


class LoginStatusMixin:
    """登录状态 Mixin

    适用于登录日志模型，表示登录结果，使用 LoginStatusConst 常量
    """
    status = Column(Boolean, nullable=False, comment="登录状态（使用 LoginStatusConst 常量：True=成功，False=失败）")


class SortMixin:
    """排序字段 Mixin

    适用于需要排序的模型，提供统一的排序字段
    """
    sort = Column(Integer, default=0, comment="排序")


class SystemMixin:
    """系统标识 Mixin

    适用于需要区分系统内置和自定义的模型，系统内置数据不允许修改和删除
    """
    is_system = Column(Boolean, default=False, comment="系统内置标识：系统内置数据不允许修改删除")


class ResourceOwnerMixin:
    """资源归属 Mixin

    适用于需要记录资源归属的模型，提供创建人用户ID/成员ID和租户ID
    """
    creator_id = Column(BigInteger, nullable=False, comment="创建人ID（平台级为用户ID，租户级为成员ID）")
    tenant_id = Column(BigInteger, nullable=True, comment="租户ID（NULL为平台级数据）")