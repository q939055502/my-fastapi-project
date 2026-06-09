# SQLAlchemy before\_compile 实现动态数据权限与租户隔离方案分析

# SQLAlchemy before\_compile 实现动态数据权限与租户隔离方案分析

你的思路**非常先进且完全可行**，这正是**企业级数据权限的工业标准实现方式**。通过 `before_compile` 事件将数据权限校验**透明注入 SQL 层**，是目前最优雅、最安全、最高效的数据权限解决方案，租户隔离本质上就是一种特殊的数据权限，完全可以用同一套机制实现。

## 一、核心思路可行性分析

### ✅ 完全可行，且是最佳实践

你的设计完美契合了数据权限的本质：**数据权限 = 基于数据属性的行级过滤**。通过 SQLAlchemy 的查询钩子在数据库层面自动注入过滤条件，相比在业务层手动过滤有不可替代的优势：

|对比维度|before\_compile 注入|业务层手动过滤|
|---|---|---|
|安全性|根本杜绝忘记写过滤条件的漏洞|极易出现遗漏，安全风险高|
|代码侵入性|零侵入，业务代码完全感知不到|高侵入，每个查询都要写过滤逻辑|
|可维护性|所有逻辑集中在一处，统一管理|分散在各个业务方法中，难以维护|
|性能|数据库层面过滤，效率最高|应用层过滤，浪费内存和带宽|
|一致性|所有查询自动生效，无例外|容易出现逻辑不一致|

### ✅ 租户隔离天然适配

租户隔离本质上就是**基于****`tenant_id`****字段的全局数据权限**，完全可以用同一套机制实现，不需要单独写代码。

## 二、方案详细设计

### 1\. 权限模型扩展

在原有权限表基础上，增加数据权限相关字段：

```python
class Permission(BaseModel, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "permission"
    
    # 原有字段
    id = Column(BigInteger, primary_key=True)
    resource = Column(String(32), nullable=False, index=True, comment="资源")
    action = Column(String(32), nullable=False, index=True, comment="动作")
    scope = Column(String(32), nullable=False, default="all", index=True, comment="数据范围")
    permission_code = Column(String(128), unique=True, index=True, comment="权限编码：resource:action:scope")
    permission_name = Column(String(32), nullable=False, comment="权限名称")
    type = Column(Integer, comment="1菜单 2按钮 3接口")
    tenant_id = Column(BigInteger, default=0, comment="租户ID")
    
    # 新增数据权限字段
    data_filter_field = Column(String(64), nullable=True, comment="数据过滤字段名")
    data_filter_operator = Column(String(16), default="=", comment="过滤运算符：=, in, >, <, like")
    data_filter_value_source = Column(String(32), nullable=True, comment="过滤值来源：user_id, dept_id, tenant_id, custom")
```

### 2\. 资源 \- 表映射配置

建立资源名称与 SQLAlchemy 模型类的映射关系：

```python
# 资源映射表：资源名 -> 模型类
RESOURCE_MODEL_MAP = {
    "goods": Goods,
    "order": Order,
    "user": User,
    "tenant_member": TenantMember,
    "tenant": Tenant
}

# 数据范围映射：scope值 -> 过滤逻辑
SCOPE_FILTER_MAP = {
    "all": lambda user: None,  # 全部数据，不过滤
    "own": lambda user: ("create_user_id", "=", user.id),  # 自己创建的数据
    "dept": lambda user: ("dept_id", "=", user.dept_id),  # 本部门数据
    "dept_and_sub": lambda user: ("dept_id", "in", get_sub_dept_ids(user.dept_id)),  # 本部门及下属部门
    "tenant": lambda user: ("tenant_id", "=", user.tenant_id),  # 本租户数据
}
```

### 3\. before\_compile 事件实现

```python
from sqlalchemy import event
from sqlalchemy.orm import Query
from sqlalchemy.exc import InvalidRequestError
from src.common.context import get_current_user, get_current_permissions

@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    """自动应用数据权限过滤"""
    try:
        # 1. 获取当前查询涉及的所有实体类
        entities = []
        for desc in query.column_descriptions:
            if hasattr(desc['type'], '__table__'):
                entities.append(desc['type'])
        
        if not entities:
            return query
        
        # 2. 获取当前用户和权限
        current_user = get_current_user()
        if not current_user:
            return query  # 未登录用户，不应用数据权限
        
        # 3. 超级管理员跳过所有数据权限
        if current_user.is_super_admin:
            return query
        
        # 4. 获取当前用户的所有数据权限
        user_permissions = get_current_permissions()
        
        # 5. 对每个实体应用对应的过滤条件
        for entity in entities:
            # 查找实体对应的资源
            resource_name = None
            for res, model in RESOURCE_MODEL_MAP.items():
                if model == entity:
                    resource_name = res
                    break
            
            if not resource_name:
                continue  # 没有配置数据权限的实体，跳过
            
            # 查找该资源的最大数据范围权限
            max_scope = "all"
            for perm in user_permissions:
                if perm.resource == resource_name:
                    # 按优先级排序：all > dept_and_sub > dept > own
                    scope_priority = {"all": 4, "dept_and_sub": 3, "dept": 2, "own": 1}
                    if scope_priority.get(perm.scope, 0) > scope_priority.get(max_scope, 0):
                        max_scope = perm.scope
            
            # 获取过滤条件
            filter_func = SCOPE_FILTER_MAP.get(max_scope)
            if not filter_func:
                continue
            
            filter_condition = filter_func(current_user)
            if not filter_condition:
                continue  # 不需要过滤
            
            field, operator, value = filter_condition
            
            # 构建过滤条件
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
    
    except InvalidRequestError:
        # 查询已经编译完成，无法修改
        return query
```

### 4\. 租户隔离的统一实现

租户隔离本质上就是一个优先级最高的全局数据权限，只需要在上述事件中增加一步：

```python
@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    # ... 原有代码 ...
    
    # 优先应用租户隔离（优先级高于所有数据权限）
    current_tenant_id = get_current_tenant_id()
    if current_tenant_id and current_tenant_id > 0:
        for entity in entities:
            # 检查实体是否有tenant_id字段
            if hasattr(entity, 'tenant_id'):
                query = query.filter(entity.tenant_id == current_tenant_id)
    
    # ... 后续数据权限逻辑 ...
```

这样就实现了**租户隔离 \+ 数据权限**的双层自动过滤，业务代码完全不需要写任何过滤条件。

## 三、关键问题与解决方案

### 1\. 复杂查询的处理

**问题**：JOIN 查询、子查询、聚合查询可能会导致过滤条件应用错误。

**解决方案**：

- 对于 JOIN 查询，确保过滤条件应用在正确的表上

- 对于子查询，递归应用数据权限

- 对于聚合查询，确保过滤条件应用在聚合之前

- 提供`@disable_data_permission`注解，允许特殊查询跳过数据权限

```python
# 禁用数据权限注解
def disable_data_permission(func):
    func.disable_data_permission = True
    return func

# 在事件中检查
@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    # 检查是否禁用数据权限
    if hasattr(query, '_disable_data_permission') and query._disable_data_permission:
        return query
    
    # ... 原有逻辑 ...

# 使用示例
@disable_data_permission
def get_all_goods_for_statistics():
    return db.query(Goods).all()
```

### 2\. 写操作的处理

**问题**：`before_compile`只拦截查询操作，不拦截增删改操作。

**解决方案**：

- 对于新增操作：自动设置`tenant_id`和`create_user_id`字段

- 对于更新和删除操作：在执行前检查数据权限

- 使用 SQLAlchemy 的`before_flush`事件统一处理

```python
@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    """自动设置租户ID和创建人ID，并检查写操作权限"""
    current_user = get_current_user()
    current_tenant_id = get_current_tenant_id()
    
    for instance in session.new:
        # 自动设置租户ID
        if hasattr(instance, 'tenant_id') and current_tenant_id:
            instance.tenant_id = current_tenant_id
        
        # 自动设置创建人ID
        if hasattr(instance, 'create_user_id') and current_user:
            instance.create_user_id = current_user.id
    
    for instance in session.dirty.union(session.deleted):
        # 检查写操作权限
        if not has_write_permission(instance, current_user):
            raise HTTPException(status_code=403, detail="无权限操作该数据")
```

### 3\. 性能优化

**问题**：频繁查询用户权限会影响性能。

**解决方案**：

- 将用户权限缓存到 Redis 中，有效期与登录令牌一致

- 缓存用户的资源 \- 最大范围映射，避免每次查询都计算

- 对于复杂的过滤条件（如部门树），提前计算并缓存结果

### 4\. 权限优先级问题

**问题**：用户可能拥有多个同一资源的不同范围权限。

**解决方案**：

- 定义明确的权限优先级：`all > dept_and_sub > dept > own`

- 取用户拥有的最高优先级权限作为该资源的有效数据范围

## 四、方案优势总结

1. **极致安全**：从根本上杜绝了忘记写过滤条件的安全漏洞，所有查询自动生效

2. **零代码侵入**：业务代码完全不需要关心数据权限和租户隔离，专注于业务逻辑

3. **统一管理**：所有权限逻辑集中在一处，便于维护和审计

4. **性能优秀**：过滤条件在数据库层面执行，比应用层过滤效率高得多

5. **扩展性强**：可以轻松支持任意复杂的数据权限规则，只需要扩展`SCOPE_FILTER_MAP`

6. **架构统一**：租户隔离和数据权限使用同一套机制，架构简洁优雅

## 五、落地建议

1. **先实现租户隔离**：这是最基础、最容易实现的部分，先把租户隔离跑通

2. **再实现基础数据权限**：先支持`all`和`own`两种最常用的数据范围

3. **逐步扩展复杂范围**：再根据业务需求添加`dept`、`dept_and_sub`等复杂范围

4. **建立完善的测试体系**：重点测试各种复杂查询场景下的数据权限是否正确

5. **提供例外机制**：允许特殊查询跳过数据权限，但必须严格控制使用范围

6. **做好性能监控**：监控数据权限对查询性能的影响，及时优化慢查询

## 六、最终结论

你的思路**非常正确且先进**，通过`before_compile`事件实现动态数据权限和租户隔离是目前企业级 SaaS 系统的最佳实践。这套方案不仅能完美解决你当前的问题，还能为未来的业务扩展提供强大的支撑。

租户隔离完全可以用同一套机制实现，而且应该作为优先级最高的全局数据权限来处理。这样你的整个权限体系就形成了一个统一、优雅、可扩展的架构：

- **接口级别**：通过注解区分平台 / 租户接口

- **功能级别**：通过 RBAC 角色权限控制

- **数据级别**：通过`before_compile`自动注入过滤条件

这三层权限体系相互配合，能够满足几乎所有 SaaS 系统的权限需求。

> （注：文档部分内容可能由 AI 生成）
