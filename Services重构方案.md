# Services 重构方案

## 一、现状分析

### 1.1 当前目录结构

```
src/services/
├── __init__.py
├── base_service.py
└── sys/                    # 命名不规范，应与 models/schemas/repositories 对齐
    ├── __init__.py
    ├── audit_log_service.py
    ├── auth_service.py
    ├── dept_service.py
    ├── file_mapping_service.py
    ├── resource_service.py
    ├── role_service.py
    ├── system_config_service.py
    ├── tenant_plan_service.py
    ├── tenant_service.py
    ├── user_service.py
    └── user_tenant_service.py
```

### 1.2 各 Service 依赖分析

| Service 文件 | 依赖的 Repository | 依赖的 Schema | 建议归属 |
|-------------|------------------|--------------|---------|
| auth_service.py | user_repository, role_repository, tenant_member_repository | LoginRequest, UserCreate 等 | auth/ |
| user_service.py | user_repository, role_repository, dept_repository | UserCreate, UserUpdate | iam/ |
| role_service.py | role_repository | RoleCreate, RoleUpdate | iam/ |
| dept_service.py | dept_repository | DeptCreate, DeptUpdate | iam/ |
| resource_service.py | permission_repository | PermissionCreate, PermissionUpdate | iam/ |
| tenant_service.py | tenant_repository | TenantCreate, TenantUpdate | tenant/ |
| tenant_plan_service.py | tenant_plan_repository | TenantPlanCreate, TenantPlanUpdate | tenant/ |
| user_tenant_service.py | user_repository, tenant_member_repository | TenantCreate | tenant/ |
| system_config_service.py | system_config_repository | SystemConfigUpdate | system/ |
| file_mapping_service.py | file_mapping_repository, user_repository | 无 | system/ |
| audit_log_service.py | 无（直接用 model） | 无 | system/ |

### 1.3 存在的 Model 问题

**严重问题**：`src/models/iam/role.py` 中的 `Role` 模型同时定义了 `resources` 和 `permissions` 两个关系：

```python
# role.py 第 31-32 行
resources = relationship("Resource", secondary=role_resource_association, back_populates="roles")
permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")
```

但 `Resource` 模型已被删除（不存在 `src/models/iam/resource.py`），导致：
- `role_resource_association` 关联到不存在的 `iam_resource` 表
- `role_service.py` 中的 `role_obj.resources` 调用会失败

**需要用户确认**：是否需要恢复 Resource 模型，还是修改 role_service.py 使用 `permissions` 替代 `resources`。

---

## 二、重构目标

### 2.1 目录结构对齐

services 目录结构与 repositories/schemas 保持一致：

```
src/services/
├── __init__.py
├── base_service.py              # 保持不变
├── iam/                        # 平台身份权限（与 models/iam/ 对应）
│   ├── __init__.py
│   ├── user_service.py
│   ├── role_service.py
│   ├── dept_service.py
│   └── permission_service.py   # 从 resource_service.py 重命名
├── tenant/                     # 租户级（与 models/tenant/ 对应）
│   ├── __init__.py
│   ├── tenant_service.py
│   ├── tenant_plan_service.py
│   └── member_service.py       # 从 user_tenant_service.py 重命名
├── system/                     # 系统级（与 models/system/ 对应）
│   ├── __init__.py
│   ├── system_config_service.py
│   ├── file_service.py         # 从 file_mapping_service.py 重命名
│   └── audit_log_service.py
├── auth/                       # 认证（与 schemas/auth/ 对应）
│   ├── __init__.py
│   └── auth_service.py
└── common/                     # 公共（与 schemas/common/ 对应）
    ├── __init__.py
    └── base_service.py         # 从 src/services/base_service.py 移动
```

### 2.2 文件移动/重命名清单

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| sys/auth_service.py | auth/auth_service.py | 移动 |
| sys/user_service.py | iam/user_service.py | 移动 |
| sys/role_service.py | iam/role_service.py | 移动 |
| sys/dept_service.py | iam/dept_service.py | 移动 |
| sys/resource_service.py | iam/permission_service.py | 移动+重命名 |
| sys/tenant_service.py | tenant/tenant_service.py | 移动 |
| sys/tenant_plan_service.py | tenant/tenant_plan_service.py | 移动 |
| sys/user_tenant_service.py | tenant/member_service.py | 移动+重命名 |
| sys/system_config_service.py | system/system_config_service.py | 移动 |
| sys/file_mapping_service.py | system/file_service.py | 移动+重命名 |
| sys/audit_log_service.py | system/audit_log_service.py | 移动 |

---

## 三、详细变更清单

### 3.1 新建目录

| 路径 | 说明 |
|------|------|
| `src/services/iam/` | IAM 服务目录 |
| `src/services/tenant/` | 租户服务目录 |
| `src/services/system/` | 系统服务目录 |
| `src/services/auth/` | 认证服务目录 |
| `src/services/common/` | 公共服务目录 |

### 3.2 文件移动

所有 `sys/` 下的 service 文件移动到对应新目录。

### 3.3 文件重命名

| 原文件名 | 新文件名 | 原因 |
|---------|---------|------|
| resource_service.py | permission_service.py | 统一命名，反映实际功能 |
| user_tenant_service.py | member_service.py | 避免与 tenant_service 混淆 |
| file_mapping_service.py | file_service.py | 简化命名 |

### 3.4 __init__.py 设计

#### 3.4.1 src/services/__init__.py

```python
"""
Services Package - 统一导出所有 Service
"""

from .base_service import BaseService

# IAM
from .iam import (
    user_service,
    role_service,
    dept_service,
    permission_service,
)

# Tenant
from .tenant import (
    tenant_service,
    tenant_plan_service,
    member_service,
)

# System
from .system import (
    system_config_service,
    file_service,
    audit_log_service,
)

# Auth
from .auth import auth_service

__all__ = [
    # Base
    "BaseService",
    # IAM
    "user_service",
    "role_service",
    "dept_service",
    "permission_service",
    # Tenant
    "tenant_service",
    "tenant_plan_service",
    "member_service",
    # System
    "system_config_service",
    "file_service",
    "audit_log_service",
    # Auth
    "auth_service",
]
```

#### 3.4.2 src/services/iam/__init__.py

```python
from .user_service import UserService, user_service
from .role_service import RoleService, role_service
from .dept_service import DeptService, dept_service
from .permission_service import ResourceService, resource_service

__all__ = [
    "UserService",
    "user_service",
    "RoleService",
    "role_service",
    "DeptService",
    "dept_service",
    "ResourceService",
    "resource_service",
]
```

#### 3.4.3 src/services/tenant/__init__.py

```python
from .tenant_service import TenantService, tenant_service
from .tenant_plan_service import TenantPlanService, tenant_plan_service
from .member_service import UserTenantService, user_tenant_service

__all__ = [
    "TenantService",
    "tenant_service",
    "TenantPlanService",
    "tenant_plan_service",
    "UserTenantService",
    "user_tenant_service",
]
```

#### 3.4.4 src/services/system/__init__.py

```python
from .system_config_service import SystemConfigService, system_config_service
from .file_service import FileService, file_service
from .audit_log_service import AuditLogService, audit_log_service

__all__ = [
    "SystemConfigService",
    "system_config_service",
    "FileService",
    "file_service",
    "AuditLogService",
    "audit_log_service",
]
```

#### 3.4.5 src/services/auth/__init__.py

```python
from .auth_service import AuthService, auth_service

__all__ = [
    "AuthService",
    "auth_service",
]
```

---

## 四、Model 问题处理方案（需用户确认）

### 4.1 问题描述

`src/models/iam/role.py` 中存在以下代码：

```python
resources = relationship("Resource", secondary=role_resource_association, back_populates="roles")
```

但 `Resource` 模型已被删除，`role_resource_association` 关联的 `iam_resource` 表不存在。

### 4.2 方案 A：恢复 Resource 模型（推荐）

恢复 `src/models/iam/resource.py`，保持原有的 role-resource 关系。

**优点**：
- 兼容现有代码逻辑
- role_service.py 不需要修改

**缺点**：
- 与之前的重构（用 Permission 替代 Resource）冲突
- 需要同时恢复 associations.py 中的 role_resource_association

### 4.3 方案 B：修改 role_service.py 使用 permissions

修改 `src/services/iam/role_service.py`，将 `role_obj.resources` 改为 `role_obj.permissions`。

**优点**：
- 符合当前 Permission 模型设计
- 不需要恢复已删除的代码

**缺点**：
- 需要同步修改 Role 模型中的 `resources` 关系
- 需要删除 `role_resource_association`

**修改内容**：
1. 修改 `src/models/iam/role.py`：删除 `resources` 关系
2. 修改 `src/models/iam/associations.py`：删除 `role_resource_association`
3. 修改 `src/services/iam/role_service.py`：
   - `_transform_role_list` 中的 `r.type == 1/2` 改为使用 `permissions`
   - `update_role_resources` 改为 `update_role_permissions`

---

## 五、需要更新的调用方

### 5.1 API 层

API 文件中引用了 services，如：

| API 文件 | 引用的 Service |
|---------|---------------|
| src/api/v1/auth.py | auth_service |
| src/api/v1/admin/users.py | user_service |
| src/api/v1/admin/roles.py | role_service |
| ... | ... |

### 5.2 initializers 层

| 文件 | 引用的 Service |
|------|----------------|
| src/core/initializers/user_initializer.py | user_service |
| src/core/initializers/tenant_initializer.py | user_repository |

---

## 六、实施步骤

### 阶段一：创建新目录结构

1. 创建 `src/services/iam/` 目录
2. 创建 `src/services/tenant/` 目录
3. 创建 `src/services/system/` 目录
4. 创建 `src/services/auth/` 目录
5. 创建 `src/services/common/` 目录

### 阶段二：移动 Service 文件

按 3.2 节表格移动所有 service 文件到新目录。

### 阶段三：更新各模块 __init__.py

创建所有新目录的 `__init__.py` 并导出对应的 service。

### 阶段四：更新主 __init__.py

更新 `src/services/__init__.py` 统一导出。

### 阶段五：更新调用方导入路径

更新 API 层和 initializers 层中所有引用旧 service 路径的代码。

### 阶段六：处理 Model 问题（需用户确认）

根据用户选择的方案处理 role.py 中的 Resource 关系问题。

### 阶段七：清理

删除旧的 `src/services/sys/` 目录。

---

## 七、注意事项

1. **不兼容旧引用**：本次重构不兼容旧引用，所有调用方必须同步更新
2. **Model 问题需确认**：在用户确认之前，不会对 models 进行修改
3. **保持 BaseService 不变**：`src/services/base_service.py` 不需要修改
4. **单例命名冲突**：tenant 下的 `user_tenant_service` 改为 `member_service`，避免与 `tenant_service` 混淆
5. **API 层同步更新**：API 文件中的 service 导入路径需要同步更新

---

## 八、新旧路径对照表

| 旧路径 | 新路径 |
|--------|--------|
| src.services.sys.auth_service | src.services.auth.auth_service |
| src.services.sys.user_service | src.services.iam.user_service |
| src.services.sys.role_service | src.services.iam.role_service |
| src.services.sys.dept_service | src.services.iam.dept_service |
| src.services.sys.resource_service | src.services.iam.permission_service |
| src.services.sys.tenant_service | src.services.tenant.tenant_service |
| src.services.sys.tenant_plan_service | src.services.tenant.tenant_plan_service |
| src.services.sys.user_tenant_service | src.services.tenant.member_service |
| src.services.sys.system_config_service | src.services.system.system_config_service |
| src.services.sys.file_mapping_service | src.services.system.file_service |
| src.services.sys.audit_log_service | src.services.system.audit_log_service |
