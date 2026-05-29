# Core 核心模块

核心模块包含应用的基础组件和工具，是整个项目的基础设施层。

## 目录结构

```
src/core/
├── __init__.py              # 模块入口
├── app_config.py            # 应用配置初始化
├── bgtask.py                # 后台任务管理
├── config.py                # 配置类定义（Pydantic Settings）
├── constants.py             # 常量定义
├── ctx.py                   # 请求上下文管理
├── dependency.py            # 依赖注入（认证、权限等）
├── exceptions.py            # 自定义异常类
├── init_app.py              # 应用初始化（数据库、资源等）
├── middlewares.py           # 中间件定义
├── rate_limit.py            # 限流控制
├── response.py              # 统一响应封装
├── security.py              # 安全工具（密码加密等）
├── validator.py             # 参数验证工具
├── log/                     # 日志模块
│   ├── __init__.py
│   ├── log.py               # 日志配置与管理
│   └── context.py           # 日志上下文（预留）
└── storage/                 # 存储模块
    ├── __init__.py
    ├── database.py          # 数据库连接配置
    ├── file_storage.py      # 文件存储抽象
    ├── generic_repository.py # 通用数据访问层
    ├── redis.py             # Redis 连接配置
    ├── token_manager.py     # Token 管理
    └── unit_of_work.py      # 工作单元模式
```

## 模块说明

### 配置与初始化
- **config.py**: 使用 Pydantic Settings 定义配置项，支持从环境变量和 `.env` 文件读取
- **app_config.py**: 应用配置的统一管理
- **init_app.py**: 应用启动时的初始化逻辑（数据库表创建、资源初始化等）

### 安全与认证
- **dependency.py**: FastAPI 依赖注入定义，包含认证和权限控制
- **security.py**: 密码加密、JWT 处理等安全工具
- **exceptions.py**: 自定义业务异常类

### 请求处理
- **middlewares.py**: 中间件定义（安全头、审计日志、请求日志等）
- **ctx.py**: 请求上下文管理，存储请求级别的数据
- **response.py**: 统一响应格式封装

### 存储层
- **storage/database.py**: SQLAlchemy 数据库引擎和会话配置
- **storage/generic_repository.py**: 通用 CRUD 操作封装
- **storage/unit_of_work.py**: 工作单元模式，管理事务
- **storage/redis.py**: Redis 客户端配置
- **storage/token_manager.py**: Token 的存储和管理

### 工具模块
- **bgtask.py**: 后台异步任务管理
- **rate_limit.py**: API 限流控制
- **constants.py**: 全局常量定义
- **validator.py**: 自定义参数验证器

### 日志模块
- **log/log.py**: Loguru 日志配置，支持多租户和日志分类
- 日志分类: `access`(访问日志)、`error`(错误日志)、`business`(业务日志)、`security`(安全日志)、`audit`(审计日志)
