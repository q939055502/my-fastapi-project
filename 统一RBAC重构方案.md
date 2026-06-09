# 统一RBAC重构方案（融合before_compile数据权限与缓存层隔离）

## 一、方案概述

本方案融合三套方案的核心思想：
1. **统一RBAC模型**：保留 `iam_permission` 和 `iam_role`，通过权限编码前缀区分平台/租户级别
2. **before_compile动态数据权限**：利用 SQLAlchemy 的 `before_compile` 事件实现自动数据过滤
3. **缓存层权限隔离**：改造缓存管理器，自动注入租户ID、用户ID等权限维度到缓存键
4. **四层权限体系**：接口级别隔离 + 功能级别RBAC + 数据级别自动过滤 + 缓存层隔离

---

## 二、已完成工作（阶段一、二）

### 2.1 已删除的租户专属RBAC文件

| 文件路径 | 说明 |
|---------|------|
| `src/models/tenant/tenant_permission.py` | 租户权限模型 |
| `src/models/tenant/tenant_role.py` | 租户角色模型 |
| `src/models/tenant/tenant_member_role.py` | 租户成员角色关联模型 |
| `src/models/tenant/associations.py` | 租户角色权限关联表 |
| `src/modules/tenant/repository/permission_repository.py` | 租户权限仓储 |
| `src/modules/tenant/repository/role_repository.py` | 租户角色仓储 |
| `src/modules/tenant/schemas/permission.py` | 租户权限Schema |
| `src/modules/tenant/schemas/role.py` | 租户角色Schema |
| `src/modules/tenant/endpoints/permissions.py` | 租户权限接口 |
| `src/modules/tenant/endpoints/roles.py` | 租户角色接口 |

### 2.2 已修改的模型字段

| 文件 | 修改内容 |
|------|---------|
| `src/models/platform/role.py` | 添加 `scope`（platform/tenant）、`tenant_id` 字段 |
| `src/models/platform/associations.py` | `iam_user_role` 添加 `subject_id`、`subject_type` |
| `src/models/tenant/tenant_member.py` | 添加 `subject_id` 字段 |
| `src/models/tenant/tenant_invite.py` | `default_role_id` 外键改为 `iam_role.id` |
| `src/models/tenant/tenant.py` | 移除 `roles`、`permissions` 关系 |

---

## 三、核心设计

### 3.1 权限编码规范

```plaintext
# 平台级权限（全局用户使用）
platform:tenant:create      # 创建租户
platform:user:ban           # 封禁用户

# 租户级权限（租户成员使用）
tenant:goods:delete:all     # 批量删除商品
tenant:goods:delete:single  # 单个删除商品
tenant:order:export         # 导出订单
```

### 3.2 主体类型约定

| subject_type | 含义 | 主体ID来源 |
|-------------|------|-----------|
| 0 | 平台用户 | `user_id` |
| 1 | 租户成员 | `member_id` |

### 3.3 接口分类体系

| 接口类型 | 注解 | 鉴权逻辑 | 示例 |
|---------|------|---------|------|
| 完全公开 | `@public_api` | 无需登录 | 租户主页、登录接口 |
| 登录即可 | `@login_required` | 需要登录，无需权限 | 修改个人信息、退出 |
| 平台级 | `@interface_type(PLATFORM)` | 平台用户 + 权限 | 创建租户、封禁用户 |
| 租户级 | `@interface_type(TENANT)` | 租户成员 + 权限 | 删除商品、管理用户 |

### 3.4 四层权限体系架构

```plaintext
请求到达
   ↓
【第一层：接口级别隔离】通过注解区分平台/租户接口
   ↓
【第二层：功能级别RBAC】角色权限校验
   ↓
【第三层：数据级别过滤】before_compile自动注入租户隔离和数据权限
   ↓
【第四层：缓存层隔离】缓存键自动包含权限维度（tenant_id, user_id, scope）
   ↓
执行业务逻辑
```

### 3.5 数据权限模型扩展

在 `iam_permission` 表基础上增加数据权限字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `data_filter_field` | VARCHAR(64) | 数据过滤字段名 |
| `data_filter_operator` | VARCHAR(16) | 过滤运算符：=, in, >, <, like |
| `data_filter_value_source` | VARCHAR(32) | 过滤值来源：user_id, dept_id, tenant_id, custom |

### 3.6 缓存键格式规范

```plaintext
缓存键格式：cache:{resource}:{tenant_id}:{user_id}[:{scope}]:{business_key}

示例：
- 单条数据：cache:goods:1:123:id=1
- 列表数据：cache:goods:1:123:all:page=1&size=10
- 平台用户：cache:tenant:0:456:id=1
```

---

## 四、后续重构步骤

### 阶段三：修改核心认证模块

#### 4.1 修改 AuthContext

```python
# src/common/core/context/auth_context.py
@dataclass
class AuthContext:
    request_id: str = "-"
    user_id: int | None = None
    username: str = ""
    tenant_id: int | None = None
    member_id: int | None = None
    client_ip: str = "unknown"
    subject_type: int = 0  # 0=平台用户，1=租户成员
    subject_id: int | None = None  # 当前主体ID
```

#### 4.2 修改 RequestContextMiddleware

```python
# src/common/core/middlewares/context_middleware.py
async def _get_user_info(self, request: Request) -> tuple:
    # ... 现有逻辑 ...
    # 新增：根据是否有tenant_id判断主体类型
    subject_type = 1 if tenant_id else 0
    subject_id = member_id if tenant_id else user_id
    return tenant_id, user_id, member_id, username, subject_type, subject_id
```

### 阶段四：新增注解与中间件

#### 4.3 新增接口类型注解

```python
# src/common/core/auth/annotations.py
from enum import Enum
from typing import Callable

class InterfaceType(Enum):
    PLATFORM = "platform"
    TENANT = "tenant"

def interface_type(itype: InterfaceType):
    """标记接口类型（平台级/租户级）"""
    def decorator(func: Callable) -> Callable:
        func.interface_type = itype
        return func
    return decorator

def public_api(func: Callable) -> Callable:
    """标记公开接口（无需登录）"""
    func.is_public = True
    return func

def login_required(func: Callable) -> Callable:
    """标记登录即可访问接口（无需权限）"""
    func.login_required = True
    return func

def disable_data_permission(func: Callable) -> Callable:
    """禁用数据权限过滤（特殊场景使用）"""
    func.disable_data_permission = True
    return func
```

#### 4.4 新增权限校验中间件

```python
# src/common/core/middlewares/auth_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    """权限校验中间件 - 执行接口级别租户隔离和权限校验"""
    
    async def dispatch(self, request: Request, call_next):
        route = request.scope.get("route")
        if not route:
            return await call_next(request)
        
        # 1. 检查是否为公开接口
        if getattr(route.endpoint, "is_public", False):
            return await call_next(request)
        
        # 2. 获取认证上下文
        auth_ctx = request.state.auth_context
        
        # 3. 检查登录状态
        if not auth_ctx.user_id:
            raise HTTPException(status_code=401, detail="请先登录")
        
        # 4. 检查是否为登录即可访问接口
        if getattr(route.endpoint, "login_required", False):
            return await call_next(request)
        
        # 5. 获取接口类型
        itype = getattr(route.endpoint, "interface_type", InterfaceType.TENANT)
        
        # 6. 接口级别租户校验
        if itype == InterfaceType.PLATFORM:
            # 平台接口：必须无tenant_id
            if auth_ctx.tenant_id is not None:
                raise HTTPException(status_code=403, detail="无平台操作权限")
            if auth_ctx.subject_type != 0:
                raise HTTPException(status_code=403, detail="需要平台管理员身份")
        else:
            # 租户接口：必须有tenant_id和member_id
            if auth_ctx.tenant_id is None or auth_ctx.member_id is None:
                raise HTTPException(status_code=403, detail="请先选择租户身份")
            if auth_ctx.subject_type != 1:
                raise HTTPException(status_code=403, detail="需要租户成员身份")
        
        return await call_next(request)
```

### 阶段五：实现before_compile数据权限

#### 4.5 新增数据权限配置

```python
# src/common/core/auth/data_permission.py
"""数据权限配置与过滤逻辑"""
from sqlalchemy import event
from sqlalchemy.orm import Query

# 资源映射表：资源名 -> 模型类
RESOURCE_MODEL_MAP = {}

# 数据范围映射：scope值 -> 过滤逻辑
SCOPE_FILTER_MAP = {
    "all": lambda ctx: None,  # 全部数据，不过滤
    "own": lambda ctx: ("create_user_id", "=", ctx.user_id),  # 自己创建的数据
    "dept": lambda ctx: ("dept_id", "=", ctx.dept_id),  # 本部门数据
    "dept_and_sub": lambda ctx: ("dept_id", "in", get_sub_dept_ids(ctx.dept_id)),  # 本部门及下属部门
    "tenant": lambda ctx: ("tenant_id", "=", ctx.tenant_id),  # 本租户数据
}

def register_resource(resource_name: str, model_class):
    """注册资源与模型的映射关系"""
    RESOURCE_MODEL_MAP[resource_name] = model_class

@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    """自动应用数据权限过滤（包括租户隔离）"""
    try:
        # 1. 获取当前查询涉及的所有实体类
        entities = []
        for desc in query.column_descriptions:
            if hasattr(desc['type'], '__table__'):
                entities.append(desc['type'])
        
        if not entities:
            return query
        
        # 2. 获取当前认证上下文
        from src.common.core.context import get_auth_context
        ctx = get_auth_context()
        
        if not ctx.user_id:
            return query  # 未登录用户，不应用数据权限
        
        # 3. 超级管理员跳过所有数据权限
        if is_super_admin(ctx.user_id):
            return query
        
        # 4. 优先应用租户隔离（优先级最高）
        if ctx.tenant_id and ctx.tenant_id > 0:
            for entity in entities:
                if hasattr(entity, 'tenant_id'):
                    query = query.filter(entity.tenant_id == ctx.tenant_id)
        
        # 5. 应用数据权限
        user_permissions = get_user_permissions(ctx.user_id, ctx.subject_type)
        
        for entity in entities:
            resource_name = None
            for res, model in RESOURCE_MODEL_MAP.items():
                if model == entity:
                    resource_name = res
                    break
            
            if not resource_name:
                continue
            
            # 查找该资源的最大数据范围权限
            max_scope = "own"
            for perm in user_permissions:
                if perm.resource == resource_name:
                    scope_priority = {"all": 4, "dept_and_sub": 3, "dept": 2, "own": 1}
                    if scope_priority.get(perm.scope, 0) > scope_priority.get(max_scope, 0):
                        max_scope = perm.scope
            
            filter_func = SCOPE_FILTER_MAP.get(max_scope)
            if not filter_func:
                continue
            
            filter_condition = filter_func(ctx)
            if not filter_condition:
                continue
            
            field, operator, value = filter_condition
            column = getattr(entity, field)
            
            if operator == "=":
                query = query.filter(column == value)
            elif operator == "in":
                query = query.filter(column.in_(value))
            elif operator == ">":
                query = query.filter(column > value)
            elif operator == "<":
                query = query.filter(column < value)
            elif operator == "like":
                query = query.filter(column.like(value))
        
        return query
    
    except Exception:
        return query
```

#### 4.6 新增before_flush写操作处理

```python
# src/common/core/auth/data_permission.py
@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    """自动设置租户ID和创建人ID，并检查写操作权限"""
    from src.common.core.context import get_auth_context
    
    ctx = get_auth_context()
    
    for instance in session.new:
        # 自动设置租户ID
        if hasattr(instance, 'tenant_id') and ctx.tenant_id:
            instance.tenant_id = ctx.tenant_id
        
        # 自动设置创建人ID
        if hasattr(instance, 'create_user_id') and ctx.user_id:
            instance.create_user_id = ctx.user_id
    
    for instance in session.dirty.union(session.deleted):
        # 检查写操作权限
        if not has_write_permission(instance, ctx):
            raise HTTPException(status_code=403, detail="无权限操作该数据")
```

### 阶段六：改造缓存管理器（核心新增）

基于现有三层缓存架构（L1本地 + L2 Redis + L3数据库）进行改造，保持原有分层设计，新增权限维度自动注入功能。

#### 4.7 修改缓存管理器 - 自动注入权限维度

```python
# src/common/core/storage/cache/cache_manager.py
class CacheManager:
    """统一缓存管理器（扩展权限维度支持）"""
    
    def _build_key_with_permission(self, resource: str, key: str, include_scope: bool = False) -> str:
        """
        自动构建包含权限维度的缓存键（核心方法）
        业务层只需要传业务key，权限维度自动注入
        
        缓存键格式：cache:{resource}:{tenant_id}:{user_id}[:{scope}]:{key}
        
        Args:
            resource: 资源名称（如goods、order）
            key: 业务层传入的key（如id=1、page=1&size=10）
            include_scope: 是否包含数据范围（列表查询必须传True）
        
        Returns:
            完整的缓存键字符串
        """
        from src.common.core.context import get_auth_context
        
        ctx = get_auth_context()
        parts = ["cache", resource]
        
        # 1. 强制添加租户ID（最高优先级，未登录/平台用户为0）
        tenant_id = ctx.tenant_id if ctx.tenant_id else "0"
        parts.append(str(tenant_id))
        
        # 2. 强制添加用户ID（个人数据隔离，未登录为anonymous）
        user_id = ctx.user_id if ctx.user_id else "anonymous"
        parts.append(str(user_id))
        
        # 3. 可选添加数据范围scope（数据权限隔离，列表查询必须传True）
        if include_scope:
            scope = get_current_user_scope(resource)
            parts.append(scope)
        
        # 4. 最后添加业务层传入的key
        parts.append(key)
        
        full_key = ":".join(parts)
        
        # 如果键太长，使用MD5哈希缩短（保留资源前缀）
        if len(full_key) > 250:
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"cache:{resource}:{key_hash}"
        
        return full_key
    
    def get_with_permission(self, resource: str, key: str, include_scope: bool = False) -> Any | None:
        """
        获取缓存（自动注入权限维度）
        
        Args:
            resource: 资源名称（如goods、order）
            key: 业务层传入的key（如id=1、page=1&size=10）
            include_scope: 是否包含数据范围（列表查询必须传True）
        
        Returns:
            缓存的值，如果未命中则返回None
        """
        full_key = self._build_key_with_permission(resource, key, include_scope)
        return self.get(full_key)
    
    def set_with_permission(self, resource: str, key: str, value: Any, 
                            l1_ttl: int | None = None, l2_ttl: int | None = None, 
                            include_scope: bool = False) -> None:
        """
        设置缓存（自动注入权限维度）
        
        Args:
            resource: 资源名称
            key: 业务层传入的key
            value: 要缓存的值
            l1_ttl: L1缓存过期时间（秒）
            l2_ttl: L2缓存过期时间（秒）
            include_scope: 是否包含数据范围
        """
        full_key = self._build_key_with_permission(resource, key, include_scope)
        self.set(full_key, value, l1_ttl, l2_ttl)
    
    def delete_by_resource(self, resource: str, key: str = None, include_scope: bool = False) -> None:
        """
        删除指定资源的缓存
        
        Args:
            resource: 资源名称
            key: 不传则删除该资源下该用户的所有缓存
            include_scope: 是否包含数据范围维度
        """
        if key:
            full_key = self._build_key_with_permission(resource, key, include_scope)
            self.delete(full_key)
        else:
            pattern = self._build_key_with_permission(resource, "*", include_scope)
            self.clear_pattern(pattern)
    
    def delete_by_user(self, user_id: int, tenant_id: int = None) -> None:
        """
        清除指定用户的所有缓存（权限变更时调用）
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID（不传则使用当前上下文的租户ID）
        """
        from src.common.core.context import get_current_tenant_id
        tenant_id = tenant_id or get_current_tenant_id() or 0
        pattern = f"cache:*:{tenant_id}:{user_id}:*"
        self.clear_pattern(pattern)
    
    def delete_by_tenant(self, tenant_id: int) -> None:
        """
        清除指定租户的所有缓存（租户删除时调用）
        
        Args:
            tenant_id: 租户ID
        """
        pattern = f"cache:*:{tenant_id}:*"
        self.clear_pattern(pattern)
```

#### 4.8 修改GenericRepository - 自动清除缓存

```python
# src/common/repository/base.py
class GenericRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic Repository Base Class（扩展缓存自动清除）"""

    def __init__(self, model: type[ModelType], resource_name: str = None):
        self.model = model
        self._has_soft_delete = self._check_soft_delete()
        self.resource_name = resource_name  # 资源名称，用于缓存管理
    
    # ... 现有CRUD方法 ...
    
    def create(
        self,
        obj_in: CreateSchemaType | dict[str, Any],
        session: Session
    ) -> ModelType:
        """创建对象（不commit）"""
        if isinstance(obj_in, dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()

        db_obj = self.model(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)
        
        # 自动清除该资源的所有列表缓存
        if self.resource_name:
            from src.common.core.storage.cache import cache_manager
            cache_manager.delete_by_resource(self.resource_name, include_scope=True)
        
        return db_obj
    
    def update(
        self,
        id: int,
        obj_in: UpdateSchemaType | dict[str, Any],
        session: Session
    ) -> ModelType | None:
        """更新对象（不commit）"""
        db_obj = self.get(id, session)
        if not db_obj:
            return None

        if hasattr(db_obj, 'is_system') and db_obj.is_system:
            raise ValueError("系统内置对象不可修改")

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            if field in PROTECTED_SYSTEM_FIELDS:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.flush()
        session.refresh(db_obj)
        
        # 自动清除单条缓存和列表缓存
        if self.resource_name:
            from src.common.core.storage.cache import cache_manager
            cache_manager.delete_by_resource(self.resource_name, f"id={id}")
            cache_manager.delete_by_resource(self.resource_name, include_scope=True)
        
        return db_obj
    
    def delete(self, id: int, session: Session, hard: bool = False) -> bool:
        """删除对象（自适应删除，不commit）"""
        db_obj = self.get_by_id(id, session)
        if not db_obj:
            return False

        if hasattr(db_obj, 'is_system') and db_obj.is_system:
            raise ValueError("系统内置对象不可删除")

        if self._has_soft_delete and not hard:
            db_obj.is_deleted = True
            db_obj.delete_time = datetime.now()
        else:
            session.delete(db_obj)

        session.flush()
        
        # 自动清除单条缓存和列表缓存
        if self.resource_name:
            from src.common.core.storage.cache import cache_manager
            cache_manager.delete_by_resource(self.resource_name, f"id={id}")
            cache_manager.delete_by_resource(self.resource_name, include_scope=True)
        
        return True
```

### 阶段七：修改权限控制模块

#### 4.9 修改 PermissionControl

```python
# src/common/core/auth/dependency.py
class PermissionControl:
    @classmethod
    def has_permission(
        cls,
        request: Request,
        permission_code: str,
        current_user: object = Depends(AuthControl.is_authed),
    ) -> None:
        """统一权限校验入口"""
        auth_ctx = request.state.auth_context
        
        # 权限前缀校验
        if permission_code.startswith("platform:"):
            if auth_ctx.subject_type != 0:
                raise BusinessException(ResponseCode.FORBIDDEN, "无平台权限")
        elif permission_code.startswith("tenant:"):
            if auth_ctx.subject_type != 1:
                raise BusinessException(ResponseCode.FORBIDDEN, "无租户权限")
        
        # 使用 subject_id 和 subject_type 查询权限
        # ... 权限查询逻辑 ...
```

### 阶段八：更新业务模块

#### 4.10 更新平台模块

- 修改 Role/Permission Service 支持租户级角色管理
- 更新角色分配逻辑支持 `subject_type`
- 注册业务模型到资源映射表
- 更新 Repository 初始化时传入资源名称

---

## 五、数据库迁移脚本（剩余部分）

```sql
-- 1. 修改 iam_role 表（已在代码中完成）
ALTER TABLE iam_role ADD COLUMN scope VARCHAR(20) DEFAULT 'platform';
ALTER TABLE iam_role ADD COLUMN tenant_id BIGINT DEFAULT 0;
CREATE INDEX idx_iam_role_scope ON iam_role(scope);
CREATE INDEX idx_iam_role_tenant_id ON iam_role(tenant_id);

-- 2. 修改 iam_user_role 关联表（已在代码中完成）
ALTER TABLE iam_user_role ADD COLUMN subject_id BIGINT;
ALTER TABLE iam_user_role ADD COLUMN subject_type INT DEFAULT 0;
UPDATE iam_user_role SET subject_id = user_id, subject_type = 0;

-- 3. 修改 tenant_member 表（已在代码中完成）
ALTER TABLE tenant_member ADD COLUMN subject_id BIGINT;
UPDATE tenant_member SET subject_id = id;

-- 4. 修改 tenant_invite 表的外键（已在代码中完成）
ALTER TABLE tenant_invite DROP CONSTRAINT IF EXISTS tenant_invite_default_role_id_fkey;
ALTER TABLE tenant_invite ADD CONSTRAINT tenant_invite_default_role_id_fkey FOREIGN KEY (default_role_id) REFERENCES iam_role(id);

-- 5. 删除租户专属表（已完成）
DROP TABLE IF EXISTS tenant_role_permission;
DROP TABLE IF EXISTS tenant_member_role;
DROP TABLE IF EXISTS tenant_role;
DROP TABLE IF EXISTS tenant_permission;

-- 6. 新增数据权限字段到 iam_permission 表
ALTER TABLE iam_permission ADD COLUMN data_filter_field VARCHAR(64);
ALTER TABLE iam_permission ADD COLUMN data_filter_operator VARCHAR(16) DEFAULT '=';
ALTER TABLE iam_permission ADD COLUMN data_filter_value_source VARCHAR(32);
```

---

## 六、API 变更

### 6.1 新增接口

| 接口 | 说明 |
|------|------|
| `POST /api/v1/tenant/get-by-domain` | 根据域名查询租户信息 |

### 6.2 修改接口

| 接口 | 修改内容 |
|------|---------|
| `POST /api/v1/roles` | 新增 `scope` 和 `tenant_id` 参数 |
| `POST /api/v1/roles/{role_id}/assign` | 新增 `subject_type` 参数 |
| `POST /api/v1/permissions` | 新增 `scope` 参数及数据权限字段 |

### 6.3 删除接口

| 接口 | 说明 |
|------|------|
| `POST /api/v1/tenant/roles` | 租户角色创建（已合并到平台接口） |
| `POST /api/v1/tenant/permissions` | 租户权限创建（已合并到平台接口） |

---

## 七、缓存层安全红线（必须严格遵守）

1. **所有缓存必须通过缓存管理器访问**，绝对禁止业务层直接使用`redis`客户端或`lru_cache`

2. **缓存键的权限维度必须由缓存管理器自动生成**，业务层绝对不能手动拼接包含`tenant_id`/`user_id`的缓存键

3. **所有写操作必须通过 GenericRepository 执行**，绝对禁止业务层直接操作`db.session`进行增删改

4. **权限变更必须立即调用`delete_by_user`方法**，否则旧权限会继续生效

5. **本地缓存只能存储非敏感、低频率变更的数据**，过期时间绝对不能超过 1 分钟

6. **列表查询必须传入 `include_scope=True`**，确保数据权限隔离生效

---

## 八、方案优势总结

### 8.1 安全性
- **接口级别**：通过注解强制区分平台/租户接口
- **功能级别**：RBAC角色权限精确控制
- **数据级别**：before_compile自动注入过滤，杜绝遗漏
- **缓存级别**：自动注入权限维度，防止缓存越权

### 8.2 代码侵入性
- 业务代码完全不需要关心租户隔离和数据权限
- 所有过滤逻辑集中在一处，统一管理

### 8.3 性能优势
- 过滤条件在数据库层面执行，效率最高
- 支持缓存用户权限，减少重复查询
- 三层缓存架构保证读取性能

### 8.4 扩展性
- 轻松支持任意复杂的数据权限规则
- 资源映射可动态扩展
- 缓存层支持灵活的TTL配置

---

## 九、实施建议

### 9.1 阶段划分

| 阶段 | 时间 | 任务 |
|------|------|------|
| 阶段三 | 1-2天 | 修改核心认证模块（AuthContext、中间件） |
| 阶段四 | 1-2天 | 新增注解与权限校验中间件 |
| 阶段五 | 2-3天 | 实现before_compile数据权限 |
| 阶段六 | 2-3天 | 改造缓存管理器（自动注入权限维度） |
| 阶段七 | 1-2天 | 修改权限控制模块 |
| 阶段八 | 2-3天 | 更新业务模块 |
| 测试验证 | 2-3天 | 编写回归测试用例 |

### 9.2 落地顺序

1. **先实现租户隔离**：在 before_compile 中优先注入 tenant_id 过滤
2. **再实现缓存层隔离**：改造缓存管理器自动注入权限维度
3. **再实现基础数据权限**：支持 all/own 两种常用范围
4. **逐步扩展复杂范围**：根据业务需求添加 dept/dept_and_sub
5. **建立完善的测试体系**：测试各种复杂查询场景

---

## 十、注意事项

1. **性能监控**：监控 before_compile 对查询性能的影响
2. **例外机制**：提供 @disable_data_permission 注解处理特殊场景
3. **权限缓存**：用户权限缓存到 Redis，有效期与令牌一致
4. **事务边界**：写操作通过 before_flush 统一处理
5. **缓存一致性**：写操作后自动清除相关缓存
6. **缓存键长度**：超过250字符自动进行MD5哈希缩短

---

## 结论

本方案融合了统一RBAC模型、before_compile动态数据权限和缓存层权限隔离，形成了一套完整的四层权限体系：

- **接口级别**：通过注解区分平台/租户接口
- **功能级别**：统一RBAC角色权限控制
- **数据级别**：before_compile自动注入租户隔离和数据权限
- **缓存级别**：自动注入权限维度（tenant_id, user_id, scope），防止缓存越权

这套方案实现了零代码侵入、极致安全、高性能的数据权限管理，是企业级SaaS系统的最佳实践。