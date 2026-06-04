# 租户权限Code写入数据库的核心方案

### 一、权限 Code 写入数据库的核心方案

权限 Code 写入 `tenant_permission` 表的核心逻辑是 \\*\\*「自动注册 + 租户同步」\\*\\*，分两类场景处理：

| 权限类型    | 写入时机           | 说明                                          |
| ------- | -------------- | ------------------------------------------- |
| 系统内置权限  | 项目初始化 / 租户创建时  | 如设计里的 `profile:view`、`user:create`，属于租户基础权限 |
| 业务自定义权限 | 项目启动扫描 / 版本更新时 | 如 `product:delete`（删除商品），属于业务接口对应的权限        |

### 二、项目启动感知接口并自动注册权限

以 Python + FastAPI/Flask 为例，通过「接口注解 + 启动扫描 + 数据库同步」实现接口权限的自动感知和注册：

#### 1. 步骤 1：定义权限注解（标记接口的权限元信息）

给接口添加装饰器，标记该接口对应的权限 Code、名称、类型等信息：

```python
from functools import wraps
from fastapi import APIRouter

router = APIRouter(prefix="/product", tags=["商品管理"])

# 定义租户权限注解（挂载权限信息到接口函数）
def tenant_permission(code: str, name: str, type: str = "api", parent_id: int = None):
    def decorator(func):
        # 将权限信息绑定到函数属性，供后续扫描
        func._tenant_perm = {
            "code": code,       # 权限Code（严格遵循「资源:操作」）
            "name": name,       # 权限名称
            "type": type,       # 类型：menu/button/api
            "parent_id": parent_id  # 父权限ID（可选，用于构建权限树）
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 给「删除商品接口」添加权限注解
@router.delete("/{product_id}", summary="删除商品")
@tenant_permission(code="product:delete", name="删除商品", type="api")
async def delete_product(product_id: int):
    # 业务逻辑：删除商品
    return {"status": "success", "product_id": product_id}
```

#### 2. 步骤 2：项目启动时扫描接口，同步权限到数据库

在项目启动钩子中，扫描所有带权限注解的接口，自动将权限信息写入 `tenant_permission`（先写「权限模板」，租户创建时复制）：

```python
from sqlalchemy.orm import Session
from src.models.tenant.tenant_permission import TenantPermission
from src.db.session import get_db
from fastapi import FastAPI

app = FastAPI()

def scan_and_register_permissions():
    """启动时扫描接口权限，同步到tenant_permission表"""
    db: Session = next(get_db())
    # 步骤1：扫描所有路由，提取权限信息
    permission_list = []
    for route in app.routes:
        # 过滤带权限注解的接口
        if hasattr(route.endpoint, "_tenant_perm"):
            permission_list.append(route.endpoint._tenant_perm)
    
    # 步骤2：写入「权限模板」（tenant_id=0 作为全局模板，租户创建时复制）
    template_tenant_id = 0
    for perm in permission_list:
        # 避免重复写入（按 tenant_id + code 唯一约束）
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
    
    # 步骤3：同步现有租户的权限（可选，版本更新时给老租户加新权限）
    # tenants = db.query(Tenant).filter(Tenant.is_deleted == 0).all()
    # for tenant in tenants:
    #     for perm in permission_list:
    #         if not db.query(TenantPermission).filter(
    #             TenantPermission.tenant_id == tenant.id,
    #             TenantPermission.code == perm["code"],
    #             TenantPermission.is_deleted == 0
    #         ).first():
    #             db.add(TenantPermission(
    #                 tenant_id=tenant.id,
    #                 name=perm["name"],
    #                 code=perm["code"],
    #                 type=perm["type"],
    #                 parent_id=perm["parent_id"]
    #             ))

    db.commit()
    db.close()

# FastAPI启动钩子：执行权限扫描
@app.on_event("startup")
async def startup():
    scan_and_register_permissions()
    # 其他启动逻辑...
```

#### 3. 步骤 3：租户创建时同步权限模板

新租户创建时，从「全局权限模板（tenant\_id=0）」复制所有权限到该租户的 `tenant_permission` 表：

```python
def create_tenant(db: Session, tenant_name: str):
    # 1. 创建租户主记录
    new_tenant = Tenant(name=tenant_name)
    db.add(new_tenant)
    db.flush()  # 触发ID生成
    
    # 2. 复制权限模板到该租户
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
    
    # 3. 初始化租户内置角色（如tenant_owner）并绑定所有权限
    # ...（省略角色创建、角色-权限绑定逻辑）
    
    db.commit()
    return new_tenant
```

### 三、前端获取权限列表的逻辑

前端在「角色分配 / 权限管理」页面，通过调用后端接口获取当前租户的所有权限，核心流程：

#### 1. 后端提供「获取租户权限列表」接口

```python
@router.get("/tenant/permissions", summary="获取租户权限列表")
async def get_tenant_permissions(
    tenant_id: int = Depends(get_current_tenant_id),  # 从请求中解析当前租户ID
    db: Session = Depends(get_db)
):
    # 查询当前租户的所有权限（软删除过滤）
    perms = db.query(TenantPermission).filter(
        TenantPermission.tenant_id == tenant_id,
        TenantPermission.is_deleted == 0
    ).order_by(TenantPermission.sort).all()
    
    # 构建树形结构（方便前端展示层级，如菜单→按钮→API）
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

#### 2. 前端使用流程

1. 进入「权限管理」页面，调用上述接口，获取当前租户的全量权限列表；
2. 以树形结构展示（如「商品管理」菜单 →「删除商品」API 权限）；
3. 管理员给角色勾选权限后，后端将「角色 - 权限」关联写入 `tenant_role_permission_association` 表；
4. 新增接口后，项目重启会自动注册权限到数据库，前端刷新即可看到新权限项（如 `product:delete`）。

### 四、关键补充说明

#### 1. 非接口类权限（如菜单 / 按钮）的处理

如果是菜单 / 按钮权限（无对应接口），可通过 `yaml` 配置文件维护，启动时和接口注解的权限一起扫描：

```yaml
# config/tenant_permissions.yaml
- code: product:menu
  name: 商品管理菜单
  type: menu
  parent_id: null
- code: product:delete_btn
  name: 删除商品按钮
  type: button
  parent_id: ${product:menu的ID}
```

#### 2. 权限校验（确保接口仅被有权限的用户调用）

接口调用时，校验当前租户成员的角色是否绑定该权限 Code：

```python
def check_permission(tenant_id: int, member_id: int, perm_code: str, db: Session):
    """校验租户成员是否有指定权限"""
    # 1. 获取成员的所有角色ID
    member = db.query(TenantMember).filter(
        TenantMember.tenant_id == tenant_id,
        TenantMember.id == member_id,
        TenantMember.is_deleted == 0
    ).first()
    if not member:
        return False
    
    # 2. 检查角色是否绑定该权限
    role_ids = [r.id for r in member.roles]
    has_perm = db.query(tenant_role_permission_association).join(
        TenantPermission, tenant_role_permission_association.c.tenant_permission_id == TenantPermission.id
    ).filter(
        tenant_role_permission_association.c.tenant_role_id.in_(role_ids),
        TenantPermission.code == perm_code,
        TenantPermission.tenant_id == tenant_id,
        TenantPermission.is_deleted == 0
    ).first()
    return has_perm is not None

# 接口中校验
@router.delete("/{product_id}")
@tenant_permission(code="product:delete", name="删除商品", type="api")
async def delete_product(
    product_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    member_id: int = Depends(get_current_member_id),
    db: Session = Depends(get_db)
):
    if not check_permission(tenant_id, member_id, "product:delete", db):
        raise HTTPException(status_code=403, detail="无删除商品权限")
    # 业务逻辑...
```

#### 3. 核心注意点

- **租户隔离**：所有权限操作必须带 `tenant_id` 过滤，禁止跨租户读写权限；
- **软删除**：权限不物理删除，仅标记 `is_deleted=1`，避免角色 - 权限关联失效；
- **Code 规范**：严格遵循「资源：操作」格式（如 `product:delete`、`order:list`），避免混乱；
- **手动兜底**：若自动扫描失败，可提供「权限手动录入 / 导入」接口，供运维补充。

### 总结

新增接口后，通过「注解标记 → 启动扫描 → 模板同步 → 租户复制」的流程，能自动将权限 Code 写入 `tenant_permission` 表；前端调用「获取权限列表」接口即可感知新权限，最终实现 “接口新增 → 权限自动注册 → 前端可分配” 的闭环。

> （注：文档部分内容可能由 AI 生成）

