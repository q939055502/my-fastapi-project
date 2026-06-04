class TenantPermission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin):
    """租户权限表"""
    __tablename__ = "tenant_permission"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, index=True, comment="权限编码（唯一，格式：资源:操作，如 user:create）")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    parent_id = Column(BigInteger, ForeignKey("tenant_permission.id"), nullable=True, index=True, comment="父级权限ID")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_tenant_permission_code'),
    )

    # 关系
    tenant = relationship("Tenant")
    parent = relationship("TenantPermission", remote_side=[id])
    children = relationship("TenantPermission", back_populates="parent")
    roles = relationship("TenantRole", secondary=tenant_role_permission_association, back_populates="permissions")