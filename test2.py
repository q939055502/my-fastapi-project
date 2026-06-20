# ✅ 方式1：直接 Depends（当前项目用的）
@router.post("/")
def create_user(
    current_user = Depends(AuthControl.is_authed),  # 显式注入
    _: None = Depends(PermissionControl.has_permission),
):
    pass

# ✅ 方式2：装饰器工厂 + Depends（语法更简洁）
def require_auth():
    return Depends(AuthControl.is_authed)

def require_permission(code: str):
    return Depends(lambda: PermissionControl.has_permission(permission_code=code))

@router.post("/")
@require_auth()
@require_permission("user:create")
def create_user():
    pass


# ❌ 错误
dependencies=[Depends(require_auth), Depends(require_permission("user:create"))]

# ✅ 正确（传函数/可调用对象）
dependencies=[require_auth, require_permission("user:create")]
dependencies=[require_auth, require_permission.has_permission()]



@router.post("/", dependencies=[require_auth, require_permission("user:create")])
def create_user():
    pass

# 请求 → 全局中间件（基础鉴权/上下文注入）
#      ↓
# 接口 → 依赖注入（精确权限检查）
#      ↓
# 数据 → 数据层（数据权限过滤）












@router.post("/", dependencies=[require_auth(), require_permission("user:create")])
def create_user():
    pass

@router.post("/")
def create_user(
    current_user = Depends(AuthControl.is_authed),
    _: None = Depends(PermissionControl.has_permission),
):
    pass