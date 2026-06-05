# Schemas 重构方案

## 一、现状分析

### 1.1 当前目录结构

```
src/schemas/
├── __init__.py           # 导出 BaseSchema, Success, Fail
├── base.py               # BaseSchema, Success, Fail
└── sys/                  # 系统级 Schema（命名不规范）
    ├── depts.py          # 部门
    ├── login.py          # 登录相关（认证相关）
    ├── resource.py       # 资源（旧设计）
    ├── roles.py          # 平台角色
    ├── system_config.py  # 系统配置
    ├── tenant.py         # 租户（命名不准确）
    ├── tenant_plan.py    # 租户套餐
    └── users.py          # 用户
```

### 1.2 当前 models 目录结构

```
src/models/
├── base.py
├── iam/                  # 平台级身份权限
│   ├── user.py
│   ├── role.py
│   ├── permission.py     # 权限（重构后）
│   ├── dept.py
│   └── associations.py
├── tenant/               # 租户级
│   ├── tenant.py
│   ├── tenant_member.py
│   ├── tenant_role.py
│   ├── tenant_permission.py
│   ├── tenant_invite.py
│   ├── tenant_dict_type.py
│   ├── tenant_dict_data.py
│   └── ...
├── system/               # 系统级
│   ├── dict_type.py
│   ├── dict_data.py
│   └── ...
└── order/                # 订单
```

### 1.3 存在的问题

| 问题 | 说明 |
|------|------|
| **目录命名不一致** | schemas 用 `sys/`，models 用 `iam/`/`tenant/`/`system/` |
| **缺少租户级 schema** | models 有 tenant_member/role/permission/invite/dict，schemas 没有对应 |
| **认证相关散落** | login.py 在 sys/ 下，应该独立为 auth/ |
| **base.py 冗余** | Success/Fail 与 core/response/response_model.py 的 ApiResponse 功能重叠 |
| **命名歧义** | sys/tenant.py 实际是租户套餐，不是租户本身 |
| **resource.py 过时** | 旧设计，已被 permission.py 替代 |

---

## 二、重构目标

### 2.1 目录结构对齐 models

schemas 目录结构与 models 保持一一对应：

```
src/schemas/
├── __init__.py
├── base.py               # 基础 Schema 类
├── iam/                  # 平台级身份权限（与 models/iam/ 对应）
│   ├── __init__.py
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   └── dept.py
├── tenant/               # 租户级（与 models/tenant/ 对应）
│   ├── __init__.py
│   ├── tenant.py         # 租户主体
│   ├── tenant_plan.py    # 租户套餐
│   ├── member.py         # 租户成员
│   ├── role.py          # 租户角色
│   ├── permission.py     # 租户权限
│   ├── invite.py         # 邀请/申请
│   ├── dict_type.py      # 租户字典类型
│   └── dict_data.py      # 租户字典数据
├── system/               # 系统级（与 models/system/ 对应）
│   ├── __init__.py
│   ├── dict_type.py      # 平台字典类型
│   ├── dict_data.py      # 平台字典数据
│   └── system_config.py  # 系统配置
├── auth/                  # 认证相关
│   ├── __init__.py
│   └── login.py
└── common/               # 公共响应 schema（如分页）
    ├── __init__.py
    └── pagination.py
```

### 2.2 Schema 类型对照表

| 层级 | Model | Schema | 说明 |
|------|-------|--------|------|
| **iam** | User | UserBase/Create/Update/Response | 平台用户 |
| | Role | RoleBase/Create/Update/Response | 平台角色 |
| | Permission | PermissionBase/Create/Update/Response | 平台权限 |
| | Dept | DeptBase/Create/Update/Response | 部门 |
| **tenant** | Tenant | TenantBase/Create/Update/Response | 租户主体 |
| | TenantPlan | TenantPlanBase/Create/Update/Response | 租户套餐 |
| | TenantMember | TenantMemberBase/Create/Update/Response | 租户成员 |
| | TenantRole | TenantRoleBase/Create/Update/Response | 租户角色 |
| | TenantPermission | TenantPermissionBase/Create/Update/Response | 租户权限 |
| | TenantInvite | TenantInviteBase/Create/Update/Response | 邀请/申请 |
| | TenantDictType | TenantDictTypeBase/Create/Update/Response | 租户字典类型 |
| | TenantDictData | TenantDictDataBase/Create/Update/Response | 租户字典数据 |
| **system** | DictType | DictTypeBase/Create/Update/Response | 平台字典类型 |
| | DictData | DictDataBase/Create/Update/Response | 平台字典数据 |
| | SystemConfig | SystemConfigUpdate | 系统配置 |
| **auth** | - | LoginRequest/Response, RegisterRequest, RefreshRequest | 认证 |

---

## 三、Schema 设计规范

### 3.1 命名规范

- **请求 Schema**：`XxxCreate`（创建）、`XxxUpdate`（更新）
- **响应 Schema**：`XxxResponse`（单条）、`XxxListResponse`（列表）
- **基础 Schema**：`XxxBase`（公共字段）

### 3.2 分层设计

```
XxxBase          # 基础字段，所有 Schema 共用
    ↓
XxxCreate       # 创建时需要的字段（继承 Base）
XxxUpdate       # 更新时可选字段（字段 Optional）
XxxResponse     # 响应时返回的完整字段（继承 Base + id/timestamp）
```

### 3.3 字段类型

| 字段类型 | Pydantic 类型 | 说明 |
|----------|---------------|------|
| 枚举值 | `Literal` 或 `str` + comment | 明确枚举含义 |
| 时间 | `datetime` | ISO 格式 |
| 外键 | `int` | 关联 ID |
| 布尔 | `bool` | 禁用 0/1 |
| 列表 | `list[T]` | 泛型列表 |

### 3.4 Field 规范

```python
class XxxResponse(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="名称")
    status: int = Field(1, description="状态：1启用 0禁用")
    created_at: datetime | None = Field(None, description="创建时间")

    model_config = ConfigDict(from_attributes=True)
```

### 3.5 与 core/response 的分工

| 组件 | 职责 | 使用方式 |
|------|------|----------|
| `ApiResponse[T]` | 统一响应包装（code/msg/data/detail/request_id/timestamp） | FastAPI `response_model=ApiResponse[XxxResponse]` |
| `PaginationInfo` | 分页信息（total/page/page_size/total_pages） | success_page() 自动封装 |
| `base.py` BaseSchema | 请求/响应数据基础类（过滤系统字段） | 业务 Schema 继承 |

**核心原则**：
- Schema 只定义**业务数据字段**（不含 code/msg）
- 响应包装由 `response_model=ApiResponse[T]` 完成
- 分页响应使用 `success_page()` 自动封装

---

## 四、详细变更清单

### 4.1 新建目录/文件

| 路径 | 说明 |
|------|------|
| `src/schemas/iam/__init__.py` | iam 模块导出 |
| `src/schemas/iam/permission.py` | 平台权限 schema（新建） |
| `src/schemas/tenant/__init__.py` | tenant 模块导出 |
| `src/schemas/tenant/tenant.py` | 租户主体 schema（新建） |
| `src/schemas/tenant/member.py` | 租户成员 schema（新建） |
| `src/schemas/tenant/role.py` | 租户角色 schema（新建） |
| `src/schemas/tenant/permission.py` | 租户权限 schema（新建） |
| `src/schemas/tenant/invite.py` | 邀请/申请 schema（新建） |
| `src/schemas/tenant/dict_type.py` | 租户字典类型 schema（新建） |
| `src/schemas/tenant/dict_data.py` | 租户字典数据 schema（新建） |
| `src/schemas/system/__init__.py` | system 模块导出 |
| `src/schemas/system/dict_type.py` | 平台字典类型 schema（新建） |
| `src/schemas/system/dict_data.py` | 平台字典数据 schema（新建） |
| `src/schemas/auth/__init__.py` | auth 模块导出 |
| `src/schemas/auth/login.py` | 认证相关 schema（从 sys/login.py 移动） |
| `src/schemas/common/__init__.py` | common 模块导出 |
| `src/schemas/common/pagination.py` | 分页响应 schema（新建） |

### 4.2 修改文件

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `src/schemas/sys/roles.py` | `src/schemas/iam/role.py` | 移动 + 重构 |
| `src/schemas/sys/users.py` | `src/schemas/iam/user.py` | 移动 + 重构 |
| `src/schemas/sys/depts.py` | `src/schemas/iam/dept.py` | 移动 + 重构 |
| `src/schemas/sys/login.py` | `src/schemas/auth/login.py` | 移动 + 重构 |
| `src/schemas/sys/tenant.py` | `src/schemas/tenant/tenant_plan.py` | 移动 + 重构（实际是套餐） |
| `src/schemas/sys/tenant_plan.py` | `src/schemas/tenant/tenant_plan.py` | 合并到租户套餐 |
| `src/schemas/sys/system_config.py` | `src/schemas/system/system_config.py` | 移动 |
| `src/schemas/sys/resource.py` | - | 删除（已被 permission.py 替代） |
| `src/schemas/sys/user_tenant.py` | - | 删除（合并到 tenant/member.py） |
| `src/schemas/base.py` | `src/schemas/base.py` | 清理 Success/Fail 或标记废弃 |
| `src/schemas/__init__.py` | `src/schemas/__init__.py` | 更新导出 |

### 4.3 删除文件

| 路径 | 说明 |
|------|------|
| `src/schemas/sys/resource.py` | 旧 resource 设计，已被 permission 替代 |
| `src/schemas/sys/user_tenant.py` | 内容合并到 tenant/member.py |
| `src/schemas/sys/` 整个目录 | 拆分到 iam/tenant/system/auth/ |

---

## 五、具体 Schema 设计

### 5.1 iam/user.py（平台用户）

```python
# Request
class UserBase(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(True, description="是否激活")

class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., description="密码")
    role_ids: list[int] | None = Field(default_factory=list, description="角色ID列表")

class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, description="邮箱")
    username: str | None = Field(None, description="用户名")
    is_active: bool | None = Field(None, description="是否激活")
    role_ids: list[int] | None = Field(default_factory=list, description="角色ID列表")
    remark: str | None = Field(None, description="备注")

class UpdatePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")

# Response
class UserResponse(UserBase):
    id: int = Field(..., description="用户ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    last_login: datetime | None = Field(None, description="最后登录时间")
    roles: list | None = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)
```

### 5.2 tenant/member.py（租户成员）

```python
# Request
class TenantMemberBase(BaseModel):
    user_id: int | None = Field(None, description="用户ID")
    role: str = Field("member", description="租户内角色")
    is_owner: int = Field(0, description="是否为租户创建人：0=否，1=是")
    is_sub_account: int = Field(0, description="是否为子账号：0=否，1=是")

class TenantMemberCreate(TenantMemberBase):
    user_id: int = Field(..., description="用户ID")

class TenantMemberUpdate(BaseModel):
    role: str | None = Field(None, description="租户内角色")

class TenantMemberRoleUpdate(BaseModel):
    role_ids: list[int] = Field(..., description="角色ID列表")

# Response
class TenantMemberResponse(TenantMemberBase):
    id: int = Field(..., description="成员ID")
    tenant_id: int = Field(..., description="租户ID")
    joined_at: datetime | None = Field(None, description="加入时间")
    join_type: str | None = Field(None, description="加入方式")
    audit_status: int | None = Field(None, description="审核状态")
    user: dict | None = Field(None, description="用户信息")
    roles: list[dict] | None = Field(default_factory=list, description="角色列表")

    model_config = ConfigDict(from_attributes=True)
```

### 5.3 tenant/invite.py（邀请/申请）

```python
# Request
class InviteGenerate(BaseModel):
    invite_type: str = Field(..., description="邀请类型：private/public/apply")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_id: int | None = Field(None, description="默认角色ID")
    need_audit: int = Field(0, description="是否需要审批：0否 1是")
    expire_hours: int | None = Field(None, description="过期小时数")

class ApplyJoin(BaseModel):
    invite_code: str | None = Field(None, description="邀请码（公开链接用）")
    tenant_id: int | None = Field(None, description="租户ID（搜索申请用）")

class AuditJoin(BaseModel):
    apply_status: int = Field(..., description="申请状态：1通过 2拒绝")
    audit_remark: str | None = Field(None, description="审批备注")

# Response
class InviteResponse(BaseModel):
    id: int = Field(..., description="邀请ID")
    tenant_id: int = Field(..., description="租户ID")
    invite_type: str = Field(..., description="邀请类型")
    invite_code: str | None = Field(None, description="邀请码")
    target_contact: str | None = Field(None, description="目标联系方式")
    default_role_id: int | None = Field(None, description="默认角色ID")
    need_audit: int = Field(..., description="是否需要审批")
    status: int = Field(..., description="状态")
    creator_member_id: int | None = Field(None, description="创建者ID")
    expire_time: int | None = Field(None, description="过期时间")

    model_config = ConfigDict(from_attributes=True)
```

### 5.4 system/dict_type.py（平台字典类型）

```python
# Request
class DictTypeBase(BaseModel):
    name: str = Field(..., description="字典名称")
    code: str = Field(..., description="字典编码")
    status: int = Field(1, description="状态：1启用 0禁用")
    sort: int = Field(0, description="排序")

class DictTypeCreate(DictTypeBase):
    pass

class DictTypeUpdate(BaseModel):
    name: str | None = Field(None, description="字典名称")
    code: str | None = Field(None, description="字典编码")
    status: int | None = Field(None, description="状态")
    sort: int | None = Field(None, description="排序")

# Response
class DictTypeResponse(DictTypeBase):
    id: int = Field(..., description="字典类型ID")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)
```

### 5.5 auth/login.py（认证）

```python
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class LoginStep1Response(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    user: UserInfoSchema = Field(..., description="用户信息")
    tenants: list[TenantInfoSchema] = Field(..., description="租户列表")

class SelectTenantRequest(BaseModel):
    temp_token: str = Field(..., description="临时登录凭证")
    tenant_id: int = Field(..., description="选择的租户ID")

class LoginStep2Response(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")
```

---

## 六、base.py 清理

### 6.1 当前问题

```python
# 当前 base.py 包含与 core/response/response_model.py 重复的类
class Success(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")  # 注意：用的是 message，不是 msg
    data: Any | None = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class Fail(BaseModel):
    code: int = Field(400, description="错误码")
    message: str = Field("失败", description="错误消息")  # 注意：用的是 message
    detail: Any | None = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
```

### 6.2 问题分析

1. `Success`/`Fail` 用 `message`，`ApiResponse` 用 `msg`，不一致
2. `Success`/`Fail` 不被使用（API 返回用的是 `success()`/`fail()` 函数）
3. `message` vs `msg` 混用

### 6.3 处理方案

**方案：删除 Success/Fail，保留 BaseSchema**

```python
# src/schemas/base.py（重构后）

from typing import Any
from pydantic import BaseModel, Field, model_validator

SYSTEM_FIELDS = {"id", "is_deleted", "delete_time", "is_system", "created_at", "updated_at"}

class BaseSchema(BaseModel):
    """基础Schema类，自动过滤系统字段"""
    model_config = {"extra": "forbid"}

    @model_validator(mode="before")
    @classmethod
    def filter_system_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k not in SYSTEM_FIELDS}
        return data
```

**删除内容**：
- `Success` 类（使用 `core/response/response_model.py` 的 `success()` 函数）
- `Fail` 类（使用 `core/response/response_model.py` 的 `fail()` 函数）

---

## 七、__init__.py 更新

### 7.1 重构后 src/schemas/__init__.py

```python
"""
Schemas Package - 统一导出所有业务 Schema
"""

from src.schemas.base import BaseSchema

# IAM 平台身份权限
from src.schemas.iam import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponseItem,
    UpdatePassword,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    DeptCreate,
    DeptUpdate,
    DeptResponse,
)

# Tenant 租户级
from src.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantPlanCreate,
    TenantPlanUpdate,
    TenantPlanResponse,
    TenantMemberCreate,
    TenantMemberUpdate,
    TenantMemberResponse,
    TenantRoleCreate,
    TenantRoleUpdate,
    TenantRoleResponse,
    TenantPermissionCreate,
    TenantPermissionUpdate,
    TenantPermissionResponse,
    InviteGenerate,
    ApplyJoin,
    AuditJoin,
    InviteResponse,
    TenantDictTypeCreate,
    TenantDictTypeUpdate,
    TenantDictTypeResponse,
    TenantDictDataCreate,
    TenantDictDataUpdate,
    TenantDictDataResponse,
)

# System 系统级
from src.schemas.system import (
    DictTypeCreate,
    DictTypeUpdate,
    DictTypeResponse,
    DictDataCreate,
    DictDataUpdate,
    DictDataResponse,
    SystemConfigUpdate,
)

# Auth 认证
from src.schemas.auth import (
    LoginRequest,
    LoginStep1Response,
    LoginStep2Response,
    SelectTenantRequest,
    RegisterRequest,
    RefreshTokenRequest,
)

__all__ = [
    # Base
    "BaseSchema",
    # IAM
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponseItem",
    "UpdatePassword",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "DeptCreate",
    "DeptUpdate",
    "DeptResponse",
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "TenantPlanCreate",
    "TenantPlanUpdate",
    "TenantPlanResponse",
    "TenantMemberCreate",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantRoleCreate",
    "TenantRoleUpdate",
    "TenantRoleResponse",
    "TenantPermissionCreate",
    "TenantPermissionUpdate",
    "TenantPermissionResponse",
    "InviteGenerate",
    "ApplyJoin",
    "AuditJoin",
    "InviteResponse",
    "TenantDictTypeCreate",
    "TenantDictTypeUpdate",
    "TenantDictTypeResponse",
    "TenantDictDataCreate",
    "TenantDictDataUpdate",
    "TenantDictDataResponse",
    # System
    "DictTypeCreate",
    "DictTypeUpdate",
    "DictTypeResponse",
    "DictDataCreate",
    "DictDataUpdate",
    "DictDataResponse",
    "SystemConfigUpdate",
    # Auth
    "LoginRequest",
    "LoginStep1Response",
    "LoginStep2Response",
    "SelectTenantRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
]
```

---

## 八、实施步骤

### 阶段一：创建新目录结构

1. 创建 `src/schemas/iam/` 目录及 `__init__.py`
2. 创建 `src/schemas/tenant/` 目录及 `__init__.py`
3. 创建 `src/schemas/system/` 目录及 `__init__.py`
4. 创建 `src/schemas/auth/` 目录及 `__init__.py`
5. 创建 `src/schemas/common/` 目录及 `__init__.py`

### 阶段二：新建缺失 Schema

1. 新建 `src/schemas/iam/permission.py`
2. 新建 `src/schemas/tenant/tenant.py`
3. 新建 `src/schemas/tenant/member.py`
4. 新建 `src/schemas/tenant/role.py`
5. 新建 `src/schemas/tenant/permission.py`
6. 新建 `src/schemas/tenant/invite.py`
7. 新建 `src/schemas/tenant/dict_type.py`
8. 新建 `src/schemas/tenant/dict_data.py`
9. 新建 `src/schemas/system/dict_type.py`
10. 新建 `src/schemas/system/dict_data.py`
11. 移动 `src/schemas/sys/login.py` → `src/schemas/auth/login.py`

### 阶段三：重构现有 Schema

1. 移动 `src/schemas/sys/users.py` → `src/schemas/iam/user.py` 并清理
2. 移动 `src/schemas/sys/roles.py` → `src/schemas/iam/role.py` 并清理
3. 移动 `src/schemas/sys/depts.py` → `src/schemas/iam/dept.py` 并清理
4. 重构 `src/schemas/sys/tenant.py` → `src/schemas/tenant/tenant_plan.py`
5. 移动 `src/schemas/sys/tenant_plan.py` → `src/schemas/tenant/tenant_plan.py`（合并）
6. 移动 `src/schemas/sys/system_config.py` → `src/schemas/system/system_config.py`
7. 清理 `src/schemas/base.py`（删除 Success/Fail）

### 阶段四：更新导入

1. 更新 `src/schemas/__init__.py` 导出
2. 更新所有使用旧路径的 API 文件

### 阶段五：清理

1. 删除 `src/schemas/sys/` 整个目录
2. 删除 `src/schemas/sys/resource.py`
3. 删除 `src/schemas/sys/user_tenant.py`

---

## 九、注意事项

1. **不兼容旧引用**：本次重构不兼容旧引用，所有调用方必须同步更新
2. **分批实施**：建议按阶段实施，每阶段完成后验证功能正常
3. **API 文件同步**：API 文件中的 schema 导入路径需要同步更新
4. **保持兼容性**：base.py 的 `BaseSchema` 类继续保留，用于自动过滤系统字段
5. **统一响应**：API 响应统一使用 `ApiResponse[T]`，不再使用 Success/Fail 类
