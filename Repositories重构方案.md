# Repositories 重构方案

## 一、现状分析

### 1.1 当前目录结构

```
src/repositories/
├── __init__.py
├── base.py               # GenericRepository 基类
└── sys/                  # 系统级 Repository（命名不规范）
    ├── __init__.py
    ├── dept_repository.py
    ├── file_mapping_repository.py
    ├── resource_repository.py
    ├── role_repository.py
    ├── system_config_repository.py
    ├── tenant_plan_repository.py
    ├── tenant_repository.py
    ├── user_repository.py
    └── user_tenant_repository.py
```

### 1.2 当前 models 目录结构（参考）

```
src/models/
├── iam/                  # 平台级身份权限
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   └── dept.py
├── tenant/               # 租户级
│   ├── tenant.py
│   ├── tenant_member.py
│   ├── tenant_role.py
│   ├── tenant_permission.py
│   ├── tenant_invite.py
│   └── ...
├── system/               # 系统级
│   ├── dict_type.py
│   ├── dict_data.py
│   ├── file_mapping.py
│   └── ...
└── order/                # 订单
```

### 1.3 当前 schemas 目录结构（参考）

```
src/schemas/
├── iam/                  # 平台身份权限
├── tenant/               # 租户级
├── system/               # 系统级
├── auth/                 # 认证
└── common/               # 公共
```

### 1.4 存在的问题

| 问题 | 说明 |
|------|------|
| **目录命名不一致** | repositories 用 `sys/`，models 用 `iam/`/`tenant/`/`system/` |
| **缺少租户级 repository** | models 有 tenant_member/role/permission/invite，repositories 没有 |
| **user_tenant_repository 定位不清** | 实际是 TenantMember 的 repository，应重命名 |
| **file_mapping_repository 归属不清** | FileMapping 属于 system 模块，但 repository 在 sys/ 下 |
| **resource_repository 过时** | 旧设计，已被 permission 替代 |

---

## 二、重构目标

### 2.1 目录结构对齐 models

repositories 目录结构与 models/schemas 保持一一对应：

```
src/repositories/
├── __init__.py
├── base.py               # GenericRepository 基类（保持不变）
├── iam/                  # 平台级身份权限（与 models/iam/ 对应）
│   ├── __init__.py
│   ├── user_repository.py
│   ├── role_repository.py
│   ├── permission_repository.py
│   └── dept_repository.py
├── tenant/               # 租户级（与 models/tenant/ 对应）
│   ├── __init__.py
│   ├── tenant_repository.py
│   ├── tenant_plan_repository.py
│   ├── member_repository.py      # 新增：租户成员
│   ├── role_repository.py        # 新增：租户角色
│   ├── permission_repository.py  # 新增：租户权限
│   └── invite_repository.py      # 新增：邀请/申请
├── system/               # 系统级（与 models/system/ 对应）
│   ├── __init__.py
│   ├── dict_type_repository.py   # 新增：平台字典类型
│   ├── dict_data_repository.py   # 新增：平台字典数据
│   ├── file_mapping_repository.py
│   └── system_config_repository.py
└── order/                # 订单（与 models/order/ 对应）
    ├── __init__.py
    ├── order_repository.py       # 新增
    ├── order_payment_repository.py
    └── order_refund_repository.py
```

### 2.2 Repository 类型对照表

| 层级 | Model | Repository | 说明 |
|------|-------|------------|------|
| **iam** | User | UserRepository | 平台用户 |
| | Role | RoleRepository | 平台角色 |
| | Permission | PermissionRepository | 平台权限 |
| | Dept | DeptRepository | 部门 |
| **tenant** | Tenant | TenantRepository | 租户主体 |
| | TenantPlan | TenantPlanRepository | 租户套餐 |
| | TenantMember | TenantMemberRepository | 租户成员 |
| | TenantRole | TenantRoleRepository | 租户角色 |
| | TenantPermission | TenantPermissionRepository | 租户权限 |
| | TenantInvite | TenantInviteRepository | 邀请/申请 |
| **system** | DictType | DictTypeRepository | 平台字典类型 |
| | DictData | DictDataRepository | 平台字典数据 |
| | FileMapping | FileMappingRepository | 文件映射 |
| | SystemConfig | SystemConfigRepository | 系统配置 |

---

## 三、详细变更清单

### 3.1 新建目录/文件

| 路径 | 说明 |
|------|------|
| `src/repositories/iam/__init__.py` | iam 模块导出 |
| `src/repositories/iam/permission_repository.py` | 平台权限 repository（新建） |
| `src/repositories/tenant/__init__.py` | tenant 模块导出 |
| `src/repositories/tenant/member_repository.py` | 租户成员 repository（新建） |
| `src/repositories/tenant/role_repository.py` | 租户角色 repository（新建） |
| `src/repositories/tenant/permission_repository.py` | 租户权限 repository（新建） |
| `src/repositories/tenant/invite_repository.py` | 邀请/申请 repository（新建） |
| `src/repositories/system/__init__.py` | system 模块导出 |
| `src/repositories/system/dict_type_repository.py` | 平台字典类型 repository（新建） |
| `src/repositories/system/dict_data_repository.py` | 平台字典数据 repository（新建） |
| `src/repositories/order/__init__.py` | order 模块导出 |

### 3.2 移动文件

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/repositories/sys/user_repository.py` | `src/repositories/iam/user_repository.py` | 平台用户 |
| `src/repositories/sys/role_repository.py` | `src/repositories/iam/role_repository.py` | 平台角色 |
| `src/repositories/sys/dept_repository.py` | `src/repositories/iam/dept_repository.py` | 部门 |
| `src/repositories/sys/resource_repository.py` | `src/repositories/iam/permission_repository.py` | 重命名为权限 |
| `src/repositories/sys/tenant_repository.py` | `src/repositories/tenant/tenant_repository.py` | 租户主体 |
| `src/repositories/sys/tenant_plan_repository.py` | `src/repositories/tenant/tenant_plan_repository.py` | 租户套餐 |
| `src/repositories/sys/user_tenant_repository.py` | `src/repositories/tenant/member_repository.py` | 重命名为成员 |
| `src/repositories/sys/system_config_repository.py` | `src/repositories/system/system_config_repository.py` | 系统配置 |
| `src/repositories/sys/file_mapping_repository.py` | `src/repositories/system/file_mapping_repository.py` | 文件映射 |

### 3.3 删除文件

| 路径 | 说明 |
|------|------|
| `src/repositories/sys/` 整个目录 | 拆分到 iam/tenant/system/ |

---

## 四、Repository 设计规范

### 4.1 命名规范

- **Repository 类**：`XxxRepository`
- **单例实例**：`xxx_repository`（小写下划线）
- **文件命名**：`xxx_repository.py`

### 4.2 继承规范

```python
from src.repositories.base import GenericRepository
from src.models.iam import User
from src.schemas.iam.user import UserCreate, UserUpdate

class UserRepository(GenericRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    # 自定义方法...

user_repository = UserRepository()
```

### 4.3 方法命名规范

| 方法前缀 | 说明 | 示例 |
|----------|------|------|
| `get_` | 获取单个对象 | `get_by_email()` |
| `list_` | 获取多个对象 | `list_by_tenant()` |
| `count_` | 获取统计值 | `count_active_users()` |
| `exists_` | 检查是否存在 | `exists_by_code()` |
| `create_` | 创建对象 | `create_with_owner()` |
| `update_` | 更新对象 | `update_roles()` |
| `delete_` | 删除对象 | `delete_by_tenant()` |

### 4.4 与 core/storage 的关系

`core/storage` 提供基础设施，`repositories` 使用这些设施：

| core/storage 组件 | 用途 |
|-------------------|------|
| `TransactionManager` | 事务管理，所有 repository 操作在事务中执行 |
| `SessionLocal` | 数据库会话工厂 |
| `cache_manager` | 缓存管理（可选，repository 可集成缓存） |

**注意**：repositories 不需要修改 core/storage，只需正确使用其提供的接口。

---

## 五、具体 Repository 设计

### 5.1 iam/user_repository.py（平台用户）

```python
class UserRepository(GenericRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    # 已有方法
    def get_by_email(self, email: str, session: Session) -> User | None: ...
    def get_by_username(self, username: str, session: Session) -> User | None: ...
    def get_with_roles(self, id: int, session: Session) -> User | None: ...
    def authenticate(self, credentials: LoginRequest, session: Session) -> User: ...
    def create_user(self, obj_in: UserCreate, session: Session) -> User: ...
    def update_roles(self, user: User, role_ids: list[int], session: Session) -> None: ...
    def update_last_login(self, id: int, session: Session) -> None: ...

user_repository = UserRepository()
```

### 5.2 iam/role_repository.py（平台角色）

```python
class RoleRepository(GenericRepository[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(model=Role)

    # 已有方法
    def is_exist(self, name: str, session: Session) -> bool: ...
    def is_exist_with_deleted(self, name: str, session: Session) -> bool: ...
    def get_with_users(self, id: int, session: Session) -> Role | None: ...
    def get_with_permissions(self, id: int, session: Session) -> Role | None: ...

role_repository = RoleRepository()
```

### 5.3 iam/permission_repository.py（平台权限）

```python
class PermissionRepository(GenericRepository[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self):
        super().__init__(model=Permission)

    def get_by_code(self, code: str, session: Session) -> Permission | None: ...
    def get_tree(self, session: Session) -> list[Permission]: ...
    def get_by_type(self, type: str, session: Session) -> list[Permission]: ...

permission_repository = PermissionRepository()
```

### 5.4 tenant/member_repository.py（租户成员）

```python
class TenantMemberRepository(GenericRepository[TenantMember, TenantMemberCreate, TenantMemberUpdate]):
    def __init__(self):
        super().__init__(model=TenantMember)

    # 从 user_tenant_repository 迁移的方法
    def get_user_tenants(self, user_id: int, session: Session) -> list[dict]: ...
    def get_tenant_members(self, tenant_id: int, session: Session) -> list[dict]: ...
    def is_user_in_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool: ...
    def is_tenant_owner(self, user_id: int, tenant_id: int, session: Session) -> bool: ...
    def add_user_to_tenant(self, user_id: int, tenant_id: int, is_owner: bool, session: Session) -> None: ...
    def remove_user_from_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool: ...

tenant_member_repository = TenantMemberRepository()
```

### 5.5 tenant/role_repository.py（租户角色）

```python
class TenantRoleRepository(GenericRepository[TenantRole, TenantRoleCreate, TenantRoleUpdate]):
    def __init__(self):
        super().__init__(model=TenantRole)

    def get_by_tenant(self, tenant_id: int, session: Session) -> list[TenantRole]: ...
    def get_with_permissions(self, id: int, session: Session) -> TenantRole | None: ...
    def assign_permissions(self, role: TenantRole, permission_ids: list[int], session: Session) -> None: ...

tenant_role_repository = TenantRoleRepository()
```

### 5.6 tenant/permission_repository.py（租户权限）

```python
class TenantPermissionRepository(GenericRepository[TenantPermission, TenantPermissionCreate, TenantPermissionUpdate]):
    def __init__(self):
        super().__init__(model=TenantPermission)

    def get_by_tenant(self, tenant_id: int, session: Session) -> list[TenantPermission]: ...
    def get_tree(self, tenant_id: int, session: Session) -> list[TenantPermission]: ...
    def get_by_code(self, tenant_id: int, code: str, session: Session) -> TenantPermission | None: ...

tenant_permission_repository = TenantPermissionRepository()
```

### 5.7 tenant/invite_repository.py（邀请/申请）

```python
class TenantInviteRepository(GenericRepository[TenantInvite, TenantInviteCreate, TenantInviteUpdate]):
    def __init__(self):
        super().__init__(model=TenantInvite)

    def get_by_code(self, invite_code: str, session: Session) -> TenantInvite | None: ...
    def get_pending_applications(self, tenant_id: int, session: Session) -> list[TenantInvite]: ...
    def create_invite(self, tenant_id: int, invite_type: str, session: Session) -> TenantInvite: ...
    def accept_application(self, invite_id: int, session: Session) -> None: ...
    def reject_application(self, invite_id: int, remark: str, session: Session) -> None: ...

tenant_invite_repository = TenantInviteRepository()
```

### 5.8 system/dict_type_repository.py（平台字典类型）

```python
class DictTypeRepository(GenericRepository[DictType, DictTypeCreate, DictTypeUpdate]):
    def __init__(self):
        super().__init__(model=DictType)

    def get_by_code(self, code: str, session: Session) -> DictType | None: ...
    def get_with_data(self, code: str, session: Session) -> DictType | None: ...

dict_type_repository = DictTypeRepository()
```

### 5.9 system/dict_data_repository.py（平台字典数据）

```python
class DictDataRepository(GenericRepository[DictData, DictDataCreate, DictDataUpdate]):
    def __init__(self):
        super().__init__(model=DictData)

    def get_by_type_code(self, type_code: str, session: Session) -> list[DictData]: ...
    def get_by_value(self, type_id: int, value: str, session: Session) -> DictData | None: ...

dict_data_repository = DictDataRepository()
```

---

## 六、__init__.py 设计

### 6.1 src/repositories/__init__.py

```python
"""
Repositories Package - 统一导出所有 Repository
"""

from .base import GenericRepository

# IAM 平台身份权限
from .iam import (
    user_repository,
    role_repository,
    permission_repository,
    dept_repository,
)

# Tenant 租户级
from .tenant import (
    tenant_repository,
    tenant_plan_repository,
    tenant_member_repository,
    tenant_role_repository,
    tenant_permission_repository,
    tenant_invite_repository,
)

# System 系统级
from .system import (
    dict_type_repository,
    dict_data_repository,
    file_mapping_repository,
    system_config_repository,
)

__all__ = [
    # Base
    "GenericRepository",
    # IAM
    "user_repository",
    "role_repository",
    "permission_repository",
    "dept_repository",
    # Tenant
    "tenant_repository",
    "tenant_plan_repository",
    "tenant_member_repository",
    "tenant_role_repository",
    "tenant_permission_repository",
    "tenant_invite_repository",
    # System
    "dict_type_repository",
    "dict_data_repository",
    "file_mapping_repository",
    "system_config_repository",
]
```

### 6.2 src/repositories/iam/__init__.py

```python
from .user_repository import user_repository
from .role_repository import role_repository
from .permission_repository import permission_repository
from .dept_repository import dept_repository

__all__ = [
    "user_repository",
    "role_repository",
    "permission_repository",
    "dept_repository",
]
```

### 6.3 src/repositories/tenant/__init__.py

```python
from .tenant_repository import tenant_repository
from .tenant_plan_repository import tenant_plan_repository
from .member_repository import tenant_member_repository
from .role_repository import tenant_role_repository
from .permission_repository import tenant_permission_repository
from .invite_repository import tenant_invite_repository

__all__ = [
    "tenant_repository",
    "tenant_plan_repository",
    "tenant_member_repository",
    "tenant_role_repository",
    "tenant_permission_repository",
    "tenant_invite_repository",
]
```

### 6.4 src/repositories/system/__init__.py

```python
from .dict_type_repository import dict_type_repository
from .dict_data_repository import dict_data_repository
from .file_mapping_repository import file_mapping_repository
from .system_config_repository import system_config_repository

__all__ = [
    "dict_type_repository",
    "dict_data_repository",
    "file_mapping_repository",
    "system_config_repository",
]
```

---

## 七、实施步骤

### 阶段一：创建新目录结构

1. 创建 `src/repositories/iam/` 目录及 `__init__.py`
2. 创建 `src/repositories/tenant/` 目录及 `__init__.py`
3. 创建 `src/repositories/system/` 目录及 `__init__.py`
4. 创建 `src/repositories/order/` 目录及 `__init__.py`

### 阶段二：移动现有 Repository

1. 移动 `sys/user_repository.py` → `iam/user_repository.py`
2. 移动 `sys/role_repository.py` → `iam/role_repository.py`
3. 移动 `sys/dept_repository.py` → `iam/dept_repository.py`
4. 重命名 `sys/resource_repository.py` → `iam/permission_repository.py`
5. 移动 `sys/tenant_repository.py` → `tenant/tenant_repository.py`
6. 移动 `sys/tenant_plan_repository.py` → `tenant/tenant_plan_repository.py`
7. 重命名 `sys/user_tenant_repository.py` → `tenant/member_repository.py`
8. 移动 `sys/system_config_repository.py` → `system/system_config_repository.py`
9. 移动 `sys/file_mapping_repository.py` → `system/file_mapping_repository.py`

### 阶段三：新建缺失 Repository

1. 新建 `tenant/role_repository.py`（租户角色）
2. 新建 `tenant/permission_repository.py`（租户权限）
3. 新建 `tenant/invite_repository.py`（邀请/申请）
4. 新建 `system/dict_type_repository.py`（平台字典类型）
5. 新建 `system/dict_data_repository.py`（平台字典数据）

### 阶段四：更新导入

1. 更新 `src/repositories/__init__.py` 导出
2. 更新所有使用旧路径的 services 文件
3. 更新所有使用旧路径的 initializers 文件

### 阶段五：清理

1. 删除 `src/repositories/sys/` 整个目录

---

## 八、注意事项

1. **不兼容旧引用**：本次重构不兼容旧引用，所有调用方必须同步更新
2. **分批实施**：建议按阶段实施，每阶段完成后验证功能正常
3. **services 同步更新**：services 文件中的 repository 导入路径需要同步更新
4. **initializers 同步更新**：core/initializers 中的 repository 导入路径需要同步更新
5. **单例命名**：注意 tenant 目录下的 role_repository 实例命名为 `tenant_role_repository`，避免与 iam 下的 `role_repository` 冲突
6. **base.py 保持不变**：GenericRepository 基类不需要修改
7. **core/storage 不需要修改**：repositories 只是使用 core/storage 提供的接口

---

## 九、需要更新导入路径的文件清单

### 9.1 services 目录

| 文件 | 需要更新的导入 |
|------|----------------|
| `services/sys/auth_service.py` | user_repository, role_repository, user_tenant_repository |
| `services/sys/user_service.py` | user_repository, role_repository, dept_repository |
| `services/sys/role_service.py` | role_repository |
| `services/sys/dept_service.py` | dept_repository |
| `services/sys/tenant_service.py` | tenant_repository |
| `services/sys/tenant_plan_service.py` | tenant_plan_repository |
| `services/sys/user_tenant_service.py` | user_repository, user_tenant_repository |
| `services/sys/resource_service.py` | resource_repository |
| `services/sys/system_config_service.py` | system_config_repository |
| `services/sys/file_mapping_service.py` | file_mapping_repository, user_repository |

### 9.2 initializers 目录

| 文件 | 需要更新的导入 |
|------|----------------|
| `core/initializers/user_initializer.py` | user_repository |
| `core/initializers/tenant_initializer.py` | user_repository |

---

## 十、新旧路径对照表

| 旧路径 | 新路径 |
|--------|--------|
| `src.repositories.sys.user_repository` | `src.repositories.iam.user_repository` |
| `src.repositories.sys.role_repository` | `src.repositories.iam.role_repository` |
| `src.repositories.sys.dept_repository` | `src.repositories.iam.dept_repository` |
| `src.repositories.sys.resource_repository` | `src.repositories.iam.permission_repository` |
| `src.repositories.sys.tenant_repository` | `src.repositories.tenant.tenant_repository` |
| `src.repositories.sys.tenant_plan_repository` | `src.repositories.tenant.tenant_plan_repository` |
| `src.repositories.sys.user_tenant_repository` | `src.repositories.tenant.member_repository` |
| `src.repositories.sys.system_config_repository` | `src.repositories.system.system_config_repository` |
| `src.repositories.sys.file_mapping_repository` | `src.repositories.system.file_mapping_repository` |

---

## 十一、与 schemas 重构的对比

| 对比项 | schemas 重构 | repositories 重构 |
|--------|-------------|-------------------|
| 目录拆分 | sys/ → iam/tenant/system/auth/common/ | sys/ → iam/tenant/system/order/ |
| 新增文件 | 10+ 个 schema 文件 | 5+ 个 repository 文件 |
| 文件移动 | 主要是移动 + 重构 | 主要是移动 + 重命名 |
| 需要更新的调用方 | services/repositories/api/tests | services/initializers |
| 基础文件 | base.py 清理 Success/Fail | base.py 保持不变 |
