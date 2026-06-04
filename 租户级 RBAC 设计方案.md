# 租户级 RBAC 设计方案

## 一、设计原则

### 1.1 两套隔离
- **平台级 RBAC**：现有 `iam_*` 表，管理平台系统权限（保留不动）
- **租户级 RBAC**：新增 `tenant_*` 表，完全独立隔离，每套租户自己的权限体系

### 1.2 权限粒度
- 租户级 RBAC 只管理**租户内部**权限，不涉及平台系统权限
- 租户级资源权限与平台级资源权限完全分离

---

## 二、核心表结构设计

### 2.1 tenant_role - 租户角色表
```python
class TenantRole(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin):
    """租户角色表"""
    __tablename__ = "tenant_role"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码（唯一）")
    is_system = Column(Integer, default=0, comment="系统内置角色：0=否，1=是")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_tenant_role_code'),
    )

    # 关系
    tenant = relationship("Tenant")
    members = relationship("TenantMember", secondary=tenant_member_role_association, back_populates="roles")
    permissions = relationship("TenantPermission", secondary=tenant_role_permission_association, back_populates="roles")
```

### 2.2 tenant_permission - 租户权限表
```python
class TenantPermission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin):
    """租户权限表"""
    __tablename__ = "tenant_permission"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, index=True, comment="权限编码（唯一，格式：资源:操作，如 user:create）")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    parent_id = Column(BigInteger, ForeignKey("tenant_permission.id"), nullable=True, index=True, comment="父级权限ID")
    is_system = Column(Integer, default=0, comment="系统内置权限：0=否，1=是，系统内置权限不允许修改删除")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_tenant_permission_code'),
    )

    # 关系
    tenant = relationship("Tenant")
    parent = relationship("TenantPermission", remote_side=[id])
    children = relationship("TenantPermission", back_populates="parent")
    roles = relationship("TenantRole", secondary=tenant_role_permission_association, back_populates="permissions")
```

### 2.3 tenant_member_role_association - 租户成员角色关联表
```python
# 在 tenant/associations.py 中
tenant_member_role_association = Table(
    'tenant_member_role_association',
    Base.metadata,
    Column('tenant_member_id', BigInteger, ForeignKey('tenant_member.id'), primary_key=True, nullable=False, index=True),
    Column('tenant_role_id', BigInteger, ForeignKey('tenant_role.id'), primary_key=True, nullable=False, index=True),
)
```

### 2.4 tenant_role_permission_association - 租户角色权限关联表
```python
# 在 tenant/associations.py 中
tenant_role_permission_association = Table(
    'tenant_role_permission_association',
    Base.metadata,
    Column('tenant_role_id', BigInteger, ForeignKey('tenant_role.id'), primary_key=True, nullable=False, index=True),
    Column('tenant_permission_id', BigInteger, ForeignKey('tenant_permission.id'), primary_key=True, nullable=False, index=True),
)
```

---

## 三、内置角色与权限

### 3.1 租户默认内置角色
| 角色编码 | 角色名称 | 说明 |
|---------|---------|------|
| `tenant_owner` | 租户所有者 | 租户创建者，拥有所有权限 |
| `tenant_admin` | 租户管理员 | 可管理租户所有权限（除了转让所有者） |
| `tenant_member` | 普通成员 | 基础权限，查看/编辑自己资料 |

### 3.2 内置权限编码规范
```
# 权限编码格式：资源:操作
- profile:view         # 查看用户资料
- profile:edit         # 编辑用户资料
- user:list            # 用户列表
- user:create          # 创建用户
- user:update          # 更新用户
- user:delete          # 删除用户
- dept:list            # 部门列表
- dept:create          # 创建部门
- dept:update          # 更新部门
- dept:delete          # 删除部门
- role:list            # 角色列表
- role:create          # 创建角色
- role:update          # 更新角色
- role:delete          # 删除角色
- setting:basic        # 基础设置
- setting:security     # 安全设置
```

#### 3.2.1 格式说明
- **资源**：如 `profile`（个人资料）、`user`（用户）、`dept`（部门）、`role`（角色）、`setting`（设置）
- **操作**：如 `view`（查看）、`create`（创建）、`update`（更新）、`delete`（删除）

---

## 四、权限自动注册机制

### 4.1 权限装饰器定义
通过装饰器给接口标记权限信息，供启动时扫描：
```python
from functools import wraps

def tenant_permission(code: str, name: str, type: str = "api", parent_id: int = None):
    """租户权限装饰器，标记接口对应的权限信息"""
    def decorator(func):
        func._tenant_perm = {
            "code": code,
            "name": name,
            "type": type,
            "parent_id": parent_id
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.delete("/{user_id}", summary="删除用户")
@tenant_permission(code="user:delete", name="删除用户", type="api")
async def delete_user(user_id: int):
    # 业务逻辑
    pass
```

### 4.2 全局权限模板（tenant_id=0）
- 使用 `tenant_id=0` 作为全局权限模板，存储所有系统支持的权限
- 项目启动时，扫描所有带 `@tenant_permission` 装饰器的接口，将权限信息同步到模板表
- 新租户创建时，从模板复制所有权限到该租户的 `tenant_permission` 表

### 4.3 项目启动扫描逻辑
```python
def scan_and_register_permissions():
    """启动时扫描接口权限，同步到全局模板（tenant_id=0）"""
    db: Session = next(get_db())
    template_tenant_id = 0
    
    # 扫描所有路由，提取权限信息
    permission_list = []
    for route in app.routes:
        if hasattr(route.endpoint, "_tenant_perm"):
            permission_list.append(route.endpoint._tenant_perm)
    
    # 写入或更新权限模板
    for perm in permission_list:
        exists = db.query(TenantPermission).filter(
            TenantPermission.tenant_id == template_tenant_id,
            TenantPermission.code == perm["code"],
            TenantPermission.is_deleted == 0
        ).first()
        if not exists:
            new_perm = TenantPermission(
                tenant_id=template_tenant_id,
                name=perm["name"],
                code=perm["code"],
                type=perm["type"],
                parent_id=perm["parent_id"]
            )
            db.add(new_perm)
    
    db.commit()
    db.close()
```

### 4.4 租户创建时同步权限
```python
def create_tenant(db: Session, tenant_name: str):
    """创建租户时同步权限模板"""
    # 1. 创建租户主记录
    new_tenant = Tenant(name=tenant_name)
    db.add(new_tenant)
    db.flush()
    
    # 2. 从模板复制权限到该租户
    template_perms = db.query(TenantPermission).filter(
        TenantPermission.tenant_id == 0,
        TenantPermission.is_deleted == 0
    ).all()
    for template in template_perms:
        tenant_perm = TenantPermission(
            tenant_id=new_tenant.id,
            name=template.name,
            code=template.code,
            type=template.type,
            parent_id=template.parent_id
        )
        db.add(tenant_perm)
    
    # 3. 初始化内置角色并绑定权限
    # ... 省略角色创建逻辑
    
    db.commit()
    return new_tenant
```

---

## 五、权限校验逻辑

### 5.1 权限校验依赖
```python
def check_tenant_permission(perm_code: str):
    """校验租户成员是否有指定权限的依赖项"""
    def dependency(
        tenant_id: int = Depends(get_current_tenant_id),
        member_id: int = Depends(get_current_member_id),
        db: Session = Depends(get_db)
    ):
        # 获取成员的所有角色
        member = db.query(TenantMember).filter(
            TenantMember.tenant_id == tenant_id,
            TenantMember.id == member_id,
            TenantMember.is_deleted == 0
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="无权限访问")
        
        # 检查角色是否绑定该权限
        role_ids = [r.id for r in member.roles]
        has_perm = db.query(tenant_role_permission_association).join(
            TenantPermission,
            tenant_role_permission_association.c.tenant_permission_id == TenantPermission.id
        ).filter(
            tenant_role_permission_association.c.tenant_role_id.in_(role_ids),
            TenantPermission.code == perm_code,
            TenantPermission.tenant_id == tenant_id,
            TenantPermission.is_deleted == 0
        ).first()
        
        if not has_perm:
            raise HTTPException(status_code=403, detail=f"无权限：{perm_code}")
        
        return True
    return dependency

# 使用示例
@router.delete("/{user_id}")
@tenant_permission(code="user:delete", name="删除用户", type="api")
async def delete_user(
    user_id: int,
    _: bool = Depends(check_tenant_permission("user:delete"))
):
    # 业务逻辑
    pass
```

---

## 六、前端权限获取流程

### 6.1 获取租户权限列表接口
```python
@router.get("/permissions", summary="获取租户权限列表")
async def get_tenant_permissions(
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """获取当前租户的所有权限，返回树形结构"""
    perms = db.query(TenantPermission).filter(
        TenantPermission.tenant_id == tenant_id,
        TenantPermission.is_deleted == 0
    ).order_by(TenantPermission.sort).all()
    
    # 构建树形结构
    def build_perm_tree(perms, parent_id=None):
        tree = []
        for perm in perms:
            if perm.parent_id == parent_id:
                node = {
                    "id": perm.id,
                    "name": perm.name,
                    "code": perm.code,
                    "type": perm.type,
                    "parent_id": perm.parent_id,
                    "children": build_perm_tree(perms, perm.id)
                }
                tree.append(node)
        return tree
    
    return {
        "code": 200,
        "data": build_perm_tree(perms)
    }
```

### 6.2 前端使用流程
1. 进入「角色管理」或「权限管理」页面
2. 调用 `/permissions` 接口获取当前租户的全量权限树
3. 以树形结构展示权限列表
4. 管理员给角色勾选权限后，保存到 `tenant_role_permission_association` 表
5. 新增接口后，项目重启自动注册权限，前端刷新即可看到新权限

---

## 七、与 tenant_member 关系

### 7.1 更新 tenant_member.py
```python
class TenantMember(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    # ... 现有字段 ...

    # 新增关系
    roles = relationship("TenantRole", secondary=tenant_member_role_association, back_populates="members")
```

---

## 八、目录结构

```
src/models/tenant/
├── __init__.py
├── tenant.py
├── tenant_plan.py
├── tenant_quota.py
├── tenant_usage.py
├── tenant_hourly_usage.py
├── tenant_member.py
├── tenant_config.py
├── tenant_role.py                  # 新增
├── tenant_permission.py             # 新增
└── associations.py                  # 新增（关联表）

src/core/
└── permission_decorator.py          # 新增：权限装饰器

src/api/v1/tenant/
├── __init__.py
├── role.py                          # 新增：角色管理接口
└── permission.py                    # 新增：权限管理接口
```

---

## 九、与平台级隔离对比

| 对比项 | 平台级 RBAC | 租户级 RBAC |
|------|----------|---------|
| 表前缀 | `iam_` | `tenant_` |
| 用户来源 | `User` | `TenantMember` |
| 所有者 | 平台运营 | 租户自己 |
| 权限范围 | 平台系统 | 租户内部 |
| 数据隔离 | `tenant_id=null` 系统角色<br>`tenant_id=x` 租户角色 | `tenant_id=x` 仅属于该租户 |

---

## 十、实施步骤建议

1. 第一步：先创建关联表和模型文件
2. 第二步：实现权限装饰器和启动扫描逻辑
3. 第三步：实现租户创建时的权限同步逻辑
4. 第四步：实现权限校验依赖项
5. 第五步：实现角色/权限管理接口
6. 第六步：实现内置角色和权限的初始化逻辑

---

## 十一、注意事项

- 两套 RBAC 完全解耦，不要混用表或关系
- 租户级权限默认不允许操作平台资源
- 租户内权限校验逻辑独立，不要复用平台的权限校验逻辑
- 全局权限模板使用 tenant_id=0，禁止修改或删除
- 所有权限操作必须带 tenant_id 过滤，确保租户隔离
- 权限不物理删除，仅标记 is_deleted=1，避免角色-权限关联失效
- 权限编码严格遵循「资源:操作」格式，避免混乱
- **系统标识重要说明**：
  - `is_system=1` 的角色和权限为系统内置，**不允许修改和删除**
  - 内置角色（tenant_owner、tenant_admin、tenant_member）必须标记 is_system=1
  - 内置权限（基础权限如 user:list、user:create 等）必须标记 is_system=1
  - 删除或修改系统内置权限会导致 RBAC 系统功能异常
  - 新增的自定义角色和权限 is_system 默认为 0，可自由管理

## 十二、系统内置标识的检查逻辑

### 12.1 角色操作检查
```python
# 删除角色前检查
def delete_tenant_role(role_id: int, tenant_id: int, db: Session):
    role = db.query(TenantRole).filter(
        TenantRole.id == role_id,
        TenantRole.tenant_id == tenant_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system == 1:
        raise HTTPException(status_code=403, detail="系统内置角色不允许删除")
    # 删除逻辑...
```

### 12.2 权限操作检查
```python
# 删除权限前检查
def delete_tenant_permission(permission_id: int, tenant_id: int, db: Session):
    permission = db.query(TenantPermission).filter(
        TenantPermission.id == permission_id,
        TenantPermission.tenant_id == tenant_id
    ).first()
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    if permission.is_system == 1:
        raise HTTPException(status_code=403, detail="系统内置权限不允许删除")
    # 删除逻辑...
```
