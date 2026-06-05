# API 重构方案

## 一、现状分析

### 1.1 当前目录结构

```
src/api/v1/
├── __init__.py              # 路由聚合（已正确组织）
├── auth.py                  # 认证接口 ✅ 已注册
├── public/
│   └── info.py             # 公开接口 ✅ 已注册
├── admin/                   # 平台管理员接口 ✅ 已注册
│   ├── auditlog.py
│   ├── depts.py
│   ├── plans.py
│   ├── resources.py
│   ├── roles.py
│   ├── settings.py
│   ├── tenants.py
│   └── users.py
├── client/                  # 租户成员接口 ✅ 已注册
│   ├── members.py          # 桩代码（待完善）
│   └── tenant.py
├── common/
│   └── files.py            # 文件接口 ✅ 已注册
├── me/
│   └── profile.py          # 个人中心 ✅ 已注册
├── tenants/                 # ❌ 问题：与 admin/tenants 重复或未注册
│   ├── manage.py
│   ├── settings.py
│   └── user_tenant.py
├── user_binds.py           # 用户绑定 ✅ 已注册
├── depts.py               # ❌ 未注册，与 admin/depts.py 重复
├── roles.py               # ❌ 未注册，与 admin/roles.py 重复
├── resources.py           # ❌ 未注册，与 admin/resources.py 重复
├── users.py               # ❌ 未注册，与 admin/users.py 重复
└── tenant.py              # ❌ 未注册
```

### 1.2 发现的问题

| 问题 | 说明 |
|------|------|
| **重复路由** | `roles.py`, `depts.py`, `resources.py`, `users.py`, `tenant.py` 在 v1 根目录，与 `admin/` 下路由重复，且未在 `__init__.py` 中注册 |
| **租户RBAC缺失** | `schemas/tenant/` 下有 `role.py`, `permission.py`, `member.py`, `invite.py` 等 Schema，但缺少对应的 API 路由 |
| **tenants/目录混乱** | `tenants/manage.py`, `tenants/settings.py`, `tenants/user_tenant.py` 未正确注册到主路由 |
| **client/目录命名** | `client/` 应改为 `tenant/` 更符合租户级语义 |

---

## 二、重构目标

### 2.1 目录结构对齐

API 目录结构与 models/schemas/repositories/services 对齐：

```
src/api/v1/
├── __init__.py              # 路由聚合（需更新）
├── auth/                    # 认证（新建目录，移动 auth.py）
├── public/                  # 公开接口（已有）
├── admin/                   # 平台管理员接口（已有）
├── tenant/                  # 租户管理员接口（新建目录，整合 tenants/ 和 client/）
├── me/                      # 个人中心（已有）
├── common/                  # 公共接口（已有）
└── user_binds.py           # 用户绑定（已有）
```

### 2.2 新目录说明

| 目录 | 说明 | 对应 models | 对应 schemas |
|------|------|-------------|-------------|
| `admin/` | 平台管理员（管理所有租户） | `models/iam/`, `models/system/` | `schemas/iam/`, `schemas/system/` |
| `tenant/` | 租户管理员（管理当前租户） | `models/tenant/` | `schemas/tenant/` |
| `auth/` | 认证相关 | - | `schemas/auth/` |
| `common/` | 公共接口 | - | - |
| `public/` | 公开接口 | - | - |
| `me/` | 个人中心 | `models/iam/` | `schemas/iam/` |

---

## 三、详细变更清单

### 3.1 新建目录

| 路径 | 说明 |
|------|------|
| `src/api/v1/auth/` | 认证接口目录 |
| `src/api/v1/tenant/` | 租户级接口目录 |

### 3.2 文件移动/重命名

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/api/v1/auth.py` | `src/api/v1/auth/auth.py` | 移动到 auth 目录 |
| `src/api/v1/tenants/manage.py` | `src/api/v1/tenant/tenant_manage.py` | 整合到 tenant 目录 |
| `src/api/v1/tenants/settings.py` | `src/api/v1/tenant/settings.py` | 移动到 tenant 目录 |
| `src/api/v1/tenants/user_tenant.py` | `src/api/v1/tenant/user_tenant.py` | 移动到 tenant 目录 |
| `src/api/v1/client/members.py` | `src/api/v1/tenant/members.py` | 移动到 tenant 目录 |
| `src/api/v1/client/tenant.py` | `src/api/v1/tenant/info.py` | 移动到 tenant 目录并重命名 |

### 3.3 新增租户级 API（基于 schemas/tenant/）

| 新文件路径 | 功能 | 说明 |
|-----------|------|------|
| `src/api/v1/tenant/roles.py` | 租户角色管理 | 对应 `schemas/tenant/role.py` |
| `src/api/v1/tenant/permissions.py` | 租户权限管理 | 对应 `schemas/tenant/permission.py` |
| `src/api/v1/tenant/invite.py` | 租户邀请/申请管理 | 对应 `schemas/tenant/invite.py` |

### 3.4 删除文件

| 文件路径 | 原因 |
|---------|------|
| `src/api/v1/roles.py` | 与 `admin/roles.py` 重复，未注册 |
| `src/api/v1/depts.py` | 与 `admin/depts.py` 重复，未注册 |
| `src/api/v1/resources.py` | 与 `admin/resources.py` 重复，未注册 |
| `src/api/v1/users.py` | 与 `admin/users.py` 重复，未注册 |
| `src/api/v1/tenant.py` | 与 `tenants/manage.py` 重复，未注册 |
| `src/api/v1/client/` | 已整合到 `tenant/` 目录 |
| `src/api/v1/tenants/` | 已整合到 `tenant/` 目录 |

### 3.5 __init__.py 更新

更新 `src/api/v1/__init__.py` 中的路由注册：

```python
# ============================================================
# 🔓 公开接口（无需认证）
# ============================================================
v1_router.include_router(public_info_router, prefix="/public")
v1_router.include_router(auth_router, prefix="/auth")

# ============================================================
# 🏢 平台管理员接口（需平台权限）
# ============================================================
admin_deps = [Depends(PermissionControl.has_permission)]
v1_router.include_router(admin_tenants_router, prefix="/admin/tenants", dependencies=admin_deps)
v1_router.include_router(admin_users_router, prefix="/admin/users", dependencies=admin_deps)
v1_router.include_router(admin_roles_router, prefix="/admin/roles", dependencies=admin_deps)
v1_router.include_router(admin_depts_router, prefix="/admin/depts", dependencies=admin_deps)
v1_router.include_router(admin_resources_router, prefix="/admin/resources", dependencies=admin_deps)
v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=admin_deps)
v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=admin_deps)
v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=admin_deps)

# ============================================================
# 👥 租户管理员接口（需租户成员权限）
# ============================================================
tenant_deps = [Depends(AuthControl.is_authed)]
v1_router.include_router(tenant_info_router, prefix="/tenant/info", dependencies=tenant_deps)
v1_router.include_router(tenant_members_router, prefix="/tenant/members", dependencies=tenant_deps)
v1_router.include_router(tenant_roles_router, prefix="/tenant/roles", dependencies=tenant_deps)
v1_router.include_router(tenant_permissions_router, prefix="/tenant/permissions", dependencies=tenant_deps)
v1_router.include_router(tenant_invite_router, prefix="/tenant/invite", dependencies=tenant_deps)
v1_router.include_router(tenant_manage_router, prefix="/tenant/manage", dependencies=tenant_deps)
v1_router.include_router(tenant_settings_router, prefix="/tenant/settings", dependencies=tenant_deps)
v1_router.include_router(user_tenant_router, prefix="/tenant/user-tenants", dependencies=tenant_deps)

# ============================================================
# 👤 个人中心接口（需登录）
# ============================================================
v1_router.include_router(me_profile_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📱 用户绑定接口（需登录）
# ============================================================
v1_router.include_router(user_binds_router, prefix="/user-binds", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📄 通用文件接口（需登录）
# ============================================================
v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])
```

---

## 四、API 路由对照表

### 4.1 平台管理员路由（admin/）

| 路由前缀 | 文件 | 功能 |
|---------|------|------|
| `/admin/tenants` | `admin/tenants.py` | 租户管理 |
| `/admin/users` | `admin/users.py` | 平台用户管理 |
| `/admin/roles` | `admin/roles.py` | 平台角色管理 |
| `/admin/depts` | `admin/depts.py` | 平台部门管理 |
| `/admin/resources` | `admin/resources.py` | 平台权限管理 |
| `/admin/plans` | `admin/plans.py` | 套餐管理 |
| `/admin/auditlog` | `admin/auditlog.py` | 审计日志 |
| `/admin/settings` | `admin/settings.py` | 系统设置 |

### 4.2 租户管理员路由（tenant/）

| 路由前缀 | 文件 | 功能 | 对应 Schema |
|---------|------|------|------------|
| `/tenant/info` | `tenant/info.py` | 租户信息 | `schemas/tenant/tenant.py` |
| `/tenant/members` | `tenant/members.py` | 租户成员管理 | `schemas/tenant/member.py` |
| `/tenant/roles` | `tenant/roles.py` | 租户角色管理 | `schemas/tenant/role.py` |
| `/tenant/permissions` | `tenant/permissions.py` | 租户权限管理 | `schemas/tenant/permission.py` |
| `/tenant/invite` | `tenant/invite.py` | 邀请/申请管理 | `schemas/tenant/invite.py` |
| `/tenant/manage` | `tenant/tenant_manage.py` | 租户管理（创建等） | `schemas/tenant/tenant.py` |
| `/tenant/settings` | `tenant/settings.py` | 租户设置 | `schemas/tenant/tenant.py` |
| `/tenant/user-tenants` | `tenant/user_tenant.py` | 用户-租户关联 | - |

### 4.3 公共路由

| 路由前缀 | 文件 | 功能 |
|---------|------|------|
| `/auth/*` | `auth/auth.py` | 认证 |
| `/public/*` | `public/info.py` | 公开接口 |
| `/me/*` | `me/profile.py` | 个人中心 |
| `/user-binds` | `user_binds.py` | 用户绑定 |
| `/common/files` | `common/files.py` | 文件管理 |

---

## 五、实施步骤

### 阶段一：创建新目录

1. 创建 `src/api/v1/auth/` 目录
2. 创建 `src/api/v1/tenant/` 目录

### 阶段二：移动现有文件

1. 移动 `auth.py` → `auth/auth.py`
2. 移动并整合 `tenants/` → `tenant/`
3. 移动并整合 `client/` → `tenant/`

### 阶段三：新增租户级 API

1. 创建 `tenant/roles.py`（租户角色管理）
2. 创建 `tenant/permissions.py`（租户权限管理）
3. 创建 `tenant/invite.py`（邀请/申请管理）

### 阶段四：创建各模块 __init__.py

1. 创建 `auth/__init__.py`
2. 创建 `tenant/__init__.py`

### 阶段五：更新主 __init__.py

更新 `src/api/v1/__init__.py` 中的路由注册和导入路径

### 阶段六：删除旧文件

1. 删除 `v1/roles.py`, `v1/depts.py`, `v1/resources.py`, `v1/users.py`, `v1/tenant.py`
2. 删除 `v1/client/` 目录
3. 删除 `v1/tenants/` 目录

---

## 六、注意事项

1. **不兼容旧引用**：本次重构不兼容旧引用，所有引用必须同步更新
2. **Model/Core 不动**：本次重构不涉及 model 和 core 目录的修改
3. **Schema 已对齐**：schemas 目录已完成重构（之前已处理），本次仅处理 API 目录
4. **权限校验**：租户级接口需要添加租户成员权限校验逻辑
5. **客户端适配**：前端可能需要同步更新 API 调用路径

---

## 七、新旧路径对照表

| 旧路径 | 新路径 |
|--------|--------|
| `src.api.v1.auth` | `src.api.v1.auth.auth` |
| `src.api.v1.tenants.manage` | `src.api.v1.tenant.tenant_manage` |
| `src.api.v1.tenants.settings` | `src.api.v1.tenant.settings` |
| `src.api.v1.tenants.user_tenant` | `src.api.v1.tenant.user_tenant` |
| `src.api.v1.client.members` | `src.api.v1.tenant.members` |
| `src.api.v1.client.tenant` | `src.api.v1.tenant.info` |
| `src.api.v1.roles` | （删除） |
| `src.api.v1.depts` | （删除） |
| `src.api.v1.resources` | （删除） |
| `src.api.v1.users` | （删除） |
| `src.api.v1.tenant` | （删除） |
