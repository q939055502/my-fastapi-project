class DataScopeRule(BaseModel, TimestampMixin):
    """角色-权限-数据范围规则表
    承载所有数据维度的隔离规则：租户、部门、创建人、自定义项目等
    """
    __tablename__ = "iam_data_scope_rule"

    role_id = Column(BigInteger, ForeignKey("iam_role.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey("iam_permission.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 维度类型：tenant(租户) / dept(部门) / creator(创建人) / custom(自定义)
    dimension_type = Column(String(20), nullable=False, index=True)
    # 匹配方式：eq(等于) / in(多选) / all(全部) / tree(部门树包含下级)
    match_type = Column(String(10), nullable=False, default="eq")
    # 维度值：* 代表全部；多个用逗号分隔，如 "123,456"
    dimension_value = Column(String(255), nullable=False, default="*")

    __table_args__ = (
        # 一个角色+一个权限+一个维度类型，唯一一条规则
        UniqueConstraint('role_id', 'permission_id', 'dimension_type', name='uq_role_perm_dimension'),
    )

    role = relationship("Role", back_populates="data_scope_rules")
    permission = relationship("Permission", back_populates="data_scope_rules")

class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, UUIDModel):
    __tablename__ = "iam_role"
    __table_args__ = (
        UniqueConstraint('code', name='uq_role_code'),
        UniqueConstraint('tenant_id', 'code', name='uq_role_tenant_code'),
    )
    name = Column(String(50), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=True, index=True, comment="NULL=平台角色")
    
    # 新增：标准资源归属字段（所有业务表统一）
    creator_id = Column(BigInteger, nullable=False, comment="创建人ID")
    dept_id = Column(BigInteger, nullable=True, comment="所属部门ID（租户内）")

    role_subjects = relationship("RoleSubject", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    # 新增：关联数据范围规则
    data_scope_rules = relationship("DataScopeRule", back_populates="role", cascade="all, delete-orphan")