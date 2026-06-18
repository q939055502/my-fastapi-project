# Core 核心模块

核心模块包含应用的基础组件和工具，是整个项目的基础设施层。提供通用的技术能力支撑，不包含业务逻辑。

## 目录结构

```
src/core/
├── __init__.py                  # 模块入口
├── config.py                    # 配置类定义（Pydantic Settings）
├── constants.py                 # 常量定义
├── background_tasks/            # 后台任务管理
│   ├── __init__.py
│   ├── bgtask_context.py        # 后台任务上下文
│   └── bgtask_handler.py        # 后台任务处理器
├── base/                        # 基础组件
│   ├── __init__.py
│   ├── pagination.py            # 分页组件
│   ├── repository_base.py       # 通用数据访问层基类
│   └── schema_base.py           # 通用 Schema 基类
├── enums/                       # 枚举定义
│   └── response_code.py         # 响应状态码枚举
├── exceptions/                  # 异常处理
│   ├── __init__.py
│   ├── business.py              # 业务异常类
│   ├── common.py                # 通用异常类
│   └── handlers.py              # 异常处理器
├── log/                         # 日志模块
│   ├── __init__.py
│   ├── log.py                   # 日志配置与管理
│   └── log_context.py           # 日志上下文
├── middlewares/                 # 中间件（纯技术层）
│   ├── __init__.py
│   ├── background_middleware.py # 后台任务中间件
│   └── headers_middleware.py    # 安全响应头中间件
├── plugins/                     # 插件模块
│   ├── __init__.py
│   └── rate_limit.py            # 限流控制
├── response/                    # 响应封装
│   ├── __init__.py
│   ├── response_model.py        # 统一响应模型
│   ├── response_msg.py          # 响应消息映射
│   ├── response_msg.yaml        # 响应消息配置文件
│   └── router_config.py         # 路由响应配置
├── scheduler/                   # 定时任务
│   ├── __init__.py
│   └── scheduler.py             # 定时任务调度器
├── storage/                     # 存储模块
│   ├── __init__.py
│   ├── database.py              # 数据库连接配置
│   ├── file_storage.py          # 文件存储抽象
│   ├── transaction_manager.py   # 事务管理器
│   └── cache/                   # 缓存管理
│       ├── __init__.py
│       ├── cache_manager.py     # 统一缓存管理器（L1+L2）
│       ├── l1_local.py          # L1 本地内存缓存
│       └── l2_redis.py          # L2 Redis 分布式缓存
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── data_processor.py        # 数据处理工具
│   ├── sensitive_filter.py      # 敏感信息过滤
│   └── sensitive_word_filter.py # 敏感词过滤
└── validators/                  # 验证器
    ├── __init__.py
    └── validators.py            # 通用数据验证工具
```

## 模块说明

### 配置与常量
- **config.py**: 使用 Pydantic Settings 定义配置项，支持从环境变量和 `.env` 文件读取
- **constants.py**: 全局常量定义（正则表达式、时间格式等）

### 基础组件
- **base/pagination.py**: 分页参数和响应模型
- **base/repository_base.py**: 通用 CRUD 操作封装，所有 Repository 继承此基类
- **base/schema_base.py**: 通用 Schema 基类（包含 ID、时间戳等通用字段）

### 异常处理
- **exceptions/business.py**: 业务异常类（BusinessException），支持自定义错误码和消息
- **exceptions/common.py**: 通用异常类（DoesNotExist、SettingNotFound 等）
- **exceptions/handlers.py**: 全局异常处理器，将异常转换为统一响应格式

### 响应封装
- **response/response_model.py**: 统一响应模型（ApiResponse），支持泛型和 Swagger 文档
- **response/response_msg.py**: 响应消息映射，从 YAML 配置文件加载
- **response/router_config.py**: 默认路由响应配置（422、429、500 等）

### 存储层
- **storage/database.py**: SQLAlchemy 数据库引擎和会话配置
- **storage/file_storage.py**: 文件存储抽象接口
- **storage/transaction_manager.py**: 事务管理器，管理数据库事务
- **storage/cache/**: 二级缓存管理器（L1 本地内存 + L2 Redis）

### 中间件
- **middlewares/headers_middleware.py**: 安全响应头中间件（CSP、X-Frame-Options 等）
- **middlewares/background_middleware.py**: 后台任务中间件

### 工具模块
- **utils/data_processor.py**: 数据处理工具函数
- **utils/sensitive_filter.py**: 敏感信息过滤（手机号、身份证号脱敏）
- **utils/sensitive_word_filter.py**: 敏感词过滤

### 验证器
- **validators/validators.py**: 通用数据验证工具（手机号、邮箱、密码强度等）

### 日志模块
- **log/log.py**: Loguru 日志配置，支持上下文绑定
- **log/log_context.py**: 日志上下文管理（request_id、tenant_id、user_id 等）

### 后台任务
- **background_tasks/bgtask_handler.py**: 后台任务处理器
- **background_tasks/bgtask_context.py**: 后台任务上下文

### 定时任务
- **scheduler/scheduler.py**: APScheduler 定时任务调度器

### 插件模块
- **plugins/rate_limit.py**: 限流控制（基于 slowapi + Limiter）

## 设计原则

1. **纯技术层**: 不包含业务逻辑，不依赖 foundation 层（运行时依赖除外）
2. **单向依赖**: core 层可被 foundation 和业务模块依赖，不反向依赖
3. **通用性**: 提供可复用的基础能力，避免重复实现
4. **可配置**: 通过 config.py 和环境变量进行配置，支持多环境部署
