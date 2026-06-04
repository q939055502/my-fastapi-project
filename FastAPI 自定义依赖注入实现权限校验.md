# FastAPI 自定义依赖注入实现权限校验

我用 **FastAPI 最标准、最稳定、企业级通用**的方式教你实现！
你要的 `@require_module("report")` 效果，在 FastAPI 里用 **「自定义依赖注入」** 实现（官方推荐，比原生装饰器更适配请求、数据库、登录态）。

## 最终效果

```python
# 一行代码绑定权限，自动校验租户套餐有没有该模块
@router.post("/api/report/export", dependencies=[Depends(require_module("report"))])
def export_report():
    return "导出成功"
```

---

# 直接复制可用的完整实现（3 步搞定）

## 第一步：创建权限校验核心依赖（写一次，全系统复用）

新建文件 `common/permission.py`

```python
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db  # 你的数据库会话依赖
from models.tenant_quota import TenantQuota  # 你的租户配额表

# 核心：创建「模块权限校验」依赖
def require_module(module_code: str):
    # 闭包：接收模块编码，返回校验函数
    async def check_permission(
        request: Request,
        db: Session = Depends(get_db)
    ):
        # 1. 从请求里拿 当前租户ID（关键！）
        # 你项目里：从token、请求上下文、登录态获取 tenant_id
        tenant_id = request.state.tenant_id  # 通用写法

        # 2. 查询租户当前的配额（包含 enabled_modules）
        quota = db.query(TenantQuota).filter(
            TenantQuota.tenant_id == tenant_id
        ).first()

        if not quota:
            raise HTTPException(status_code=403, detail="未开通任何会员套餐")

        # 3. 核心校验：判断模块编码是否在白名单里
        enabled_modules = quota.enabled_modules or []
        if module_code not in enabled_modules:
            raise HTTPException(status_code=403, detail=f"无权限：需要【{module_code}】模块权限")

    return check_permission
```

---

## 第二步：接口上直接用（一行绑定权限）

```python
from fastapi import APIRouter, Depends
from common.permission import require_module

router = APIRouter()

# 报表导出接口 → 必须有 report 权限才能访问
@router.post("/api/report/export", dependencies=[Depends(require_module("report"))])
def export_report():
    return "导出成功"

# 用户管理接口 → 必须有 user 权限
@router.get("/api/user/list", dependencies=[Depends(require_module("user"))])
def user_list():
    return "用户列表"
```

---

## 第三步：把 tenant\_id 注入请求上下文（登录时执行）

你登录 / 鉴权的时候，把**当前租户 ID**塞进 `request.state`，上面的权限校验就能拿到：

```python
# 你的登录/Token校验依赖
async def get_current_tenant(request: Request, token: str = Depends(oauth2_scheme)):
    # 解析token，获取租户ID
    tenant_id = parse_token(token)
    # 塞进请求上下文
    request.state.tenant_id = tenant_id
```

---

# 工作流程（自动执行，无需手动写判断）

1. 用户请求 `/api/report/export`

2. FastAPI 自动运行 `require_module("report")`

3. 拿当前租户 ID → 查询 `tenant_quota` 表

4. 看 `enabled_modules` 里有没有 `report`

5. ✅ 有 → 放行

6. ❌ 无 → 直接返回 403 无权限

---

# 为什么这么设计？（行业标准）

1. **一行代码控制权限**，不用每个接口写重复判断

2. **和业务完全解耦**，后续加新模块只需要改编码

3. **稳定不失效**，不依赖 URL，不随接口路径变化

4. **全局统一**，所有接口权限逻辑一模一样

---

# 极简总结

`require_module("模块编码")` = **自动权限校验器**
你只需要在接口上加一行依赖，系统就会**自动判断租户套餐有没有这个功能**，完全不用手动写判断逻辑！

> （注：文档部分内容可能由 AI 生成）
