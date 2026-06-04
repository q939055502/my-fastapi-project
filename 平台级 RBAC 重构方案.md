# 平台级 RBAC 重构方案

## 一、设计原则

### 1.1 两套隔离
- **平台级 RBAC**：重构现有 `iam_*` 表，管理平台系统权限（运营/管理员）
- **租户级 RBAC**：新增 `tenant_*` 表，完全独立隔离，每套租户自己的权限体系

### 1.2 权限粒度
- 平台级 RBAC 只管理**平台系统**权限，不涉及租户内部权限
- 平台级资源权限与租户级资源权限完全分离

---

## 二、核心表结构设计（重构后）

### 2.1 iam_role - 平台角色表
```python
class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin):
    """平台角色表"""
    __tablename__ = "iam_role"

    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码（唯一）")
    is_system = Column(Integer, default=0, comment="系统内置角色：0=否，1=是")

    __table_args__ = (
        UniqueConstraint('code', name='uq_role_code'),
    )

    # 关系
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")
```

### 2.2 iam_permission - 平台权限表
```python
class Permission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin):
    """平台权限表"""
    __tablename__ = "iam_permission"

    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, index=True, comment="权限编码（唯一，格式：资源:操作，如 user:create）")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    parent_id = Column(BigInteger, ForeignKey("iam_permission.id"), nullable=True, index=True, comment="父级权限ID")
    is_system = Column(Integer, default=0, comment="系统内置权限：0=否，1=是，系统内置权限不允许修改删除")

    __table_args__ = (
        UniqueConstraint('code', name='uq_permission_code'),
    )

    # 关系
    parent = relationship("Permission", remote_side=[id])
    children = relationship("Permission", back_populates="parent")
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")
```

### 2.3 iam_user_role_association - 用户角色关联表（保留现有）
```python
# 在 iam/associations.py 中
user_role_association = Table(
    'iam_user_role',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('iam_user.id'), primary_key=True),
    Column('role_id', BigInteger, ForeignKey('iam_role.id'), primary_key=True),
    extend_existing=True,
)
```

### 2.4 iam_role_permission_association - 角色权限关联表（新增/修改）
```python
# 在 iam/associations.py 中
role_permission_association = Table(
    'iam_role_permission',
    Base.metadata,
    Column('role_id', BigInteger, ForeignKey('iam_role.id'), primary_key=True),
    Column('permission_id', BigInteger, ForeignKey('iam_permission.id'), primary_key=True),
    extend_existing=True,
)
```

---

## 三、内置角色与权限

### 3.1 平台默认内置角色
| 角色编码 | 角色名称 | 说明 |
|---------|---------|------|
| `super_admin` | 超级管理员 | 拥有所有平台权限 |
| `admin` | 平台管理员 | 拥有大部分管理权限 |
| `operator` | 运营人员 | 拥有基础运营权限 |
| `auditor` | 审计人员 | 只读权限，用于审计 |

### 3.2 内置权限编码规范
```
# 权限编码格式：资源:操作
- user:view            # 查看用户
- user:create          # 创建用户
- user:update          # 更新用户
- user:delete          # 删除用户
- role:list            # 角色列表
- role:create          # 创建角色
- role:update          # 更新角色
- role:delete          # 删除角色
- tenant:list          # 租户列表
- tenant:create        # 创建租户
- tenant:update        # 更新租户
- tenant:delete        # 删除租户
- plan:list            # 套餐列表
- plan:create          # 创建套餐
- plan:update          # 更新套餐
- plan:delete          # 删除套餐
- system:config        # 系统配置
```

#### 3.2.1 格式说明
- **资源**：如 `user`（用户）、`role`（角色）、`tenant`（租户）、`plan`（套餐）、`system`（系统）
- **操作**：如 `view`（查看）、`create`（创建）、`update`（更新）、`delete`（删除）

---

## 四、权限自动注册机制

### 4.1 权限装饰器定义
通过装饰器给接口标记权限信息，供启动时扫描：
```python
from functools import wraps

def platform_permission(code: str, name: str, type: str = "api", parent_id: int = None):
    """平台权限装饰器，标记接口对应的权限信息"""
    def decorator(func):
        func._platform_perm = {
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
@platform_permission(code="user:delete", name="删除用户", type="api")
async def delete_user(user_id: int):
    # 业务逻辑
    pass
```

### 4.2 项目启动扫描逻辑
```python
def scan_and_register_platform_permissions():
    """启动时扫描接口权限，同步到iam_permission表"""
    db: Session = next(get_db())

    # 扫描所有路由，提取权限信息
    permission_list = []
    for route in app.routes:
        if hasattr(route.endpoint, "_platform_perm"):
            permission_list.append(route.endpoint._platform_perm)

    # 写入或更新权限
    for perm in permission_list:
        exists = db.query(Permission).filter(
            Permission.code == perm["code"],
            Permission.is_deleted == 0
        ).first()
        if not exists:
            new_perm = Permission(
                name=perm["name"],
                code=perm["code"],
                type=perm["type"],
                parent_id=perm["parent_id"]
            )
            db.add(new_perm)

    db.commit()
    db.close()
```

---

## 五、权限校验逻辑

### 5.1 权限校验依赖
```python
def check_platform_permission(perm_code: str):
    """校验平台用户是否有指定权限的依赖项"""
    def dependency(
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ):
        # 获取用户的所有角色
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == 0
        ).first()
        if not user:
            raise HTTPException(status_code=403, detail="无权限访问")

        # 检查角色是否绑定该权限
        role_ids = [r.id for r in user.roles]
        has_perm = db.query(role_permission_association).join(
            Permission,
            role_permission_association.c.permission_id == Permission.id
        ).filter(
            role_permission_association.c.role_id.in_(role_ids),
            Permission.code == perm_code,
            Permission.is_deleted == 0
        ).first()

        if not has_perm:
            raise HTTPException(status_code=403, detail=f"无权限：{perm_code}")

        return True
    return dependency

# 使用示例
@router.delete("/{user_id}")
@platform_permission(code="user:delete", name="删除用户", type="api")
async def delete_user(
    user_id: int,
    _: bool = Depends(check_platform_permission("user:delete"))
):
    # 业务逻辑
    pass
```

---

## 六、前端权限获取流程

### 6.1 获取平台权限列表接口
```python
@router.get("/permissions", summary="获取平台权限列表")
async def get_platform_permissions(db: Session = Depends(get_db)):
    """获取平台的所有权限，返回树形结构"""
    perms = db.query(Permission).filter(
        Permission.is_deleted == 0
    ).order_by(Permission.sort).all()

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
2. 调用 `/permissions` 接口获取平台的全量权限树
3. 以树形结构展示权限列表
4. 管理员给角色勾选权限后，保存到 `iam_role_permission_association` 表
5. 新增接口后，项目重启自动注册权限，前端刷新即可看到新权限

---

## 七、与 User 关系

### 7.1 更新 user.py（保持现有，增加关系）
```python
class User(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    # ... 现有字段 ...

    # 新增关系（已存在）
    roles = relationship("Role", secondary=user_role_association, back_populates="users")
```

---

## 八、目录结构

```
src/models/iam/
├── __init__.py
├── user.py              # 现有：用户表
├── role.py              # 重构：平台角色表
├── permission.py        # 重构：平台权限表（原resource表）
├── dept.py              # 现有：部门表
├── user_bind.py         # 现有：用户绑定表
└── associations.py      # 重构：关联表（角色权限关联）

src/core/
└── platform_permission_decorator.py  # 新增：平台权限装饰器

src/api/v1/admin/
├── __init__.py
├── role.py                          # 重构：角色管理接口
└── permission.py                    # 新增：权限管理接口
```

---

## 九、与租户级隔离对比

| 对比项 | 平台级 RBAC | 租户级 RBAC |
|------|----------|---------|
| 表前缀 | `iam_` | `tenant_` |
| 用户来源 | `User` | `TenantMember` |
| 所有者 | 平台运营 | 租户自己 |
| 权限范围 | 平台系统 | 租户内部 |
| 权限编码 | `资源:操作` | `资源:操作` |
| 唯一约束 | `code` | `tenant_id + code` |

---

## 十、实施步骤建议

1. 第一步：先创建角色权限关联表和修改现有模型文件
2. 第二步：实现权限装饰器和启动扫描逻辑
3. 第三步：实现权限校验依赖项
4. 第四步：实现角色/权限管理接口
5. 第五步：实现内置角色和权限的初始化逻辑
6. 第六步：数据迁移（将现有iam_resource数据迁移到iam_permission）

---

## 十一、注意事项

- 两套 RBAC 完全解耦，不要混用表或关系
- 平台级权限只管理平台系统资源，不涉及租户内部
- 平台权限校验逻辑独立，不要复用租户的权限校验逻辑
- 权限编码严格遵循「资源:操作」格式，避免混乱
- 权限不物理删除，仅标记 is_deleted=1，避免角色-权限关联失效
- 迁移时注意保留现有 iam_role 中的 is_system 角色，避免影响现有功能

---

## 十三、数据迁移方案

### 13.1 iam_resource -> iam_permission 迁移
将现有 iam_resource 表中的数据迁移到 iam_permission：
- 保持现有数据结构
- 重命名表名
- 修改字段名（resource -> permission）
- 调整关系

### 12.2 iam_role 字段调整
- 保留 name, is_system 字段
- 新增 code 字段
- 移除 tenant_id 字段
- 添加 unique constraint on code
