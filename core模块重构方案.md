# src/core 模块重构方案

## 一、背景与目标

### 问题分析
当前 `src/core` 目录存在以下问题：

| 问题 | 描述 |
|------|------|
| 命名混淆 | `config.py` 和 `app_config.py` 都含"config"，易混淆 |
| 职责不清 | `settings/` 目录内容混杂（响应消息、路由配置） |
| 文件过大 | `handlers/init_app.py` 超过1000行，职责过多 |
| 扩展性差 | 初始化逻辑硬编码，新增初始化功能困难 |

### 重构目标
1. **职责清晰**：明确各模块职责，按功能分类
2. **易于维护**：拆分大文件，单一职责原则
3. **易于扩展**：模块化设计，新增功能只需添加新模块
4. **命名规范**：统一命名风格，减少混淆

---

## 二、重构方案

### 2.1 目录结构调整

**重构前：**
```
src/core/
├── config.py              # 应用配置（环境变量）
├── app_config.py          # FastAPI应用配置（中间件、异常、路由）
├── settings/              # 混杂配置（响应消息、路由配置）
│   ├── response_msg.py
│   ├── response_msg.yaml
│   └── router_config.py
└── handlers/              # 处理器（含初始化逻辑）
    ├── init_app.py        # 超大初始化文件（1000+行）
    └── ...其他处理器
```

**重构后：**
```
src/core/
├── config.py              # 应用配置（环境变量，保持不变）
├── app_setup.py           # FastAPI应用配置（重命名自app_config.py）
├── response/              # 响应相关配置（重命名自settings/）
│   ├── __init__.py
│   ├── response_msg.py    # 响应消息加载器
│   ├── response_msg.yaml  # 响应消息内容
│   └── router_config.py   # 路由默认响应配置
├── initializers/          # 初始化模块（新建）
│   ├── __init__.py        # 统一入口
│   ├── db_initializer.py  # 数据库初始化
│   ├── user_initializer.py # 用户初始化
│   ├── tenant_initializer.py # 租户相关初始化
│   ├── rbac_initializer.py  # RBAC权限体系初始化
│   ├── dict_initializer.py   # 字典初始化
│   ├── config_initializer.py # 系统配置初始化
│   └── dept_initializer.py   # 部门初始化
└── handlers/              # 处理器（移除init_app.py）
    └── ...其他处理器（保持不变）
```

### 2.2 文件职责定义

| 文件/目录 | 职责 | 状态 |
|-----------|------|------|
| `config.py` | 应用配置类（从.env读取环境变量） | 保持不变 |
| `app_setup.py` | FastAPI应用创建配置（中间件、异常处理、路由注册） | 重命名 |
| `response/` | 响应消息和路由响应配置 | 重命名 |
| `initializers/` | 应用启动初始化钩子集合 | 新建 |
| `handlers/` | 异常处理器（移除init_app.py） | 部分修改 |

### 2.3 initializers 模块设计

#### 2.3.1 目录结构
```
src/core/initializers/
├── __init__.py          # 统一入口函数
├── db_initializer.py    # 数据库表结构创建
├── user_initializer.py  # 超级管理员、测试用户创建
├── tenant_initializer.py # 租户套餐、默认租户创建
├── rbac_initializer.py  # 资源、角色、权限初始化
├── dict_initializer.py  # 字典数据初始化
├── config_initializer.py # 系统配置初始化
└── dept_initializer.py  # 部门数据初始化
```

#### 2.3.2 各模块职责

| 文件 | 职责 | 包含函数 |
|------|------|----------|
| `db_initializer.py` | 数据库表结构创建 | `init_db()` |
| `user_initializer.py` | 用户初始化 | `init_superuser()` |
| `tenant_initializer.py` | 租户相关初始化 | `init_plans()`, `init_default_tenant()` |
| `rbac_initializer.py` | RBAC权限体系初始化 | `init_resources()`, `init_roles()` |
| `dict_initializer.py` | 字典数据初始化 | `init_dict()` |
| `config_initializer.py` | 系统配置初始化 | `init_system_config()` |
| `dept_initializer.py` | 部门数据初始化 | `init_depts()` |

#### 2.3.3 统一入口 (`__init__.py`)

```python
# 统一初始化入口
def run_all_initializers():
    """按顺序执行所有初始化器"""
    from .db_initializer import init_db
    from .user_initializer import init_superuser
    from .tenant_initializer import init_plans, init_default_tenant
    from .rbac_initializer import init_resources, init_roles
    from .config_initializer import init_system_config
    from .dept_initializer import init_depts
    from .dict_initializer import init_dict
    
    init_db()
    init_superuser()
    init_plans()
    init_default_tenant()
    init_resources()
    init_roles()
    init_system_config()
    init_depts()
    init_dict()
```

---

## 三、迁移方案

### 3.1 文件重命名

| 原文件 | 新文件 | 说明 |
|--------|--------|------|
| `app_config.py` | `app_setup.py` | 文件名变更，内容不变 |
| `settings/` | `response/` | 目录重命名，内容不变 |

### 3.2 文件拆分（从 `handlers/init_app.py`）

| 原函数 | 目标文件 | 说明 |
|--------|----------|------|
| `init_db()` | `initializers/db_initializer.py` | 数据库表结构创建 |
| `init_superuser()` | `initializers/user_initializer.py` | 超级管理员创建 |
| `init_plans()` | `initializers/tenant_initializer.py` | 租户套餐创建 |
| `init_default_tenant()` | `initializers/tenant_initializer.py` | 默认租户创建 |
| `init_resources()` | `initializers/rbac_initializer.py` | 资源初始化 |
| `init_roles()` | `initializers/rbac_initializer.py` | 角色初始化 |
| `init_system_config()` | `initializers/config_initializer.py` | 系统配置初始化 |
| `init_depts()` | `initializers/dept_initializer.py` | 部门初始化 |
| `init_data()` | `initializers/__init__.py` | 统一入口 |

### 3.3 文件删除

| 文件 | 说明 |
|------|------|
| `handlers/init_app.py` | 所有功能已迁移到initializers |

### 3.4 更新调用方

| 调用位置 | 修改内容 |
|----------|----------|
| `src/__init__.py` | 从 `initializers` 导入 `run_all_initializers` |

---

## 四、实施计划

### 阶段一：创建目录结构
- [ ] 创建 `src/core/initializers/` 目录
- [ ] 创建 `src/core/response/` 目录

### 阶段二：文件重命名
- [ ] `app_config.py` → `app_setup.py`
- [ ] `settings/` → `response/`

### 阶段三：拆分初始化逻辑
- [ ] 拆分 `init_app.py` 到各初始化模块
- [ ] 创建 `initializers/__init__.py` 统一入口

### 阶段四：更新调用方
- [ ] 更新 `src/__init__.py` 中的初始化调用

### 阶段五：清理旧文件
- [ ] 删除 `handlers/init_app.py`

### 阶段六：验证测试
- [ ] 运行 ruff 检查
- [ ] 启动应用验证初始化正常

---

## 五、注意事项

1. **幂等性保证**：所有初始化函数必须保持幂等性
2. **依赖顺序**：初始化顺序需保持不变（DB → 用户 → 租户 → RBAC → 配置）
3. **向后兼容**：重构只调整代码结构，不改变功能
4. **导入路径更新**：需更新所有引用 `app_config` 和 `settings` 的地方

---

## 六、优点

| 优点 | 说明 |
|------|------|
| **模块化** | 每个初始化器职责单一，易于理解和维护 |
| **可扩展** | 新增初始化功能只需创建新文件 |
| **可复用** | 单个初始化器可以单独调用（如测试场景） |
| **清晰的依赖关系** | 入口文件明确管理执行顺序 |
| **命名规范** | 目录和文件命名更清晰，减少混淆 |
