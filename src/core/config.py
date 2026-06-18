"""
应用配置模块

使用 Pydantic V2 语法定义应用的配置项，支持从环境变量和 .env 文件读取配置。
包含应用的基本信息、CORS 配置、数据库配置、JWT 配置等。

职责划分：
- config.py: 应用配置（支持环境变量覆盖，从 constants.py 引用默认值）
- constants.py: 程序固定常量（真正固定不变的值）

配置加载优先级：
1. 环境变量（最高优先级）
2. .env 文件
3. 代码中的默认值（最低优先级）
"""

import json
import os
import secrets

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.constants import DateTimeConst


class Settings(BaseSettings):
    """
    应用配置类

    使用 Pydantic V2 的 BaseSettings 类，支持从环境变量和 .env 文件读取配置。
    所有配置项都有默认值，同时支持通过环境变量覆盖。
    """

    # ========== 应用基本配置 ==========
    VERSION: str = "1.0.0"              # 应用版本号
    APP_TITLE: str = "管理系统"          # 应用标题，用于API文档和日志
    PROJECT_NAME: str = "管理系统"       # 项目名称，用于日志和监控
    APP_DESCRIPTION: str = "业务APP + Web后端管理系统"  # 应用描述

    APP_ENV: str = "production"         # 应用环境：development | production
    DEBUG: bool = False                 # 调试模式开关，生产环境必须为False

    # ========== 存储配置 ==========
    # 存储类型：local（本地存储）| oss（阿里云OSS）| cos（腾讯云COS）
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage"              # 本地存储目录
    LOCAL_STORAGE_URL: str = "http://localhost:8000/storage"  # 本地存储访问URL

    # 阿里云OSS配置
    OSS_ACCESS_KEY_ID: str = ""                       # OSS访问密钥ID
    OSS_ACCESS_KEY_SECRET: str = ""                   # OSS访问密钥Secret
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"  # OSS地域节点
    OSS_BUCKET_NAME: str = ""                         # OSS存储桶名称

    # 腾讯云COS配置
    COS_SECRET_ID: str = ""                           # COS密钥ID
    COS_SECRET_KEY: str = ""                          # COS密钥Key
    COS_REGION: str = "ap-guangzhou"                  # COS地域
    COS_BUCKET_NAME: str = ""                         # COS存储桶名称

    # ========== CORS 配置 ==========
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"  # 允许跨域的源，多个用逗号分隔
    CORS_ALLOW_CREDENTIALS: bool = True  # 是否允许携带凭证（cookies等）
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # 允许的HTTP方法
    CORS_ALLOW_HEADERS: list = ["Content-Type", "Authorization", "X-Requested-With"]  # 允许的请求头

    # ========== 路径配置 ==========
    LOG_DIR: str = "./logs"  # 日志文件存储目录

    # ========== 日志配置 ==========
    LOG_ACCESS_RETENTION_DAYS: int = 30      # 访问日志保留天数
    LOG_ERROR_RETENTION_DAYS: int = 90       # 错误日志保留天数
    LOG_BUSINESS_RETENTION_DAYS: int = 30    # 业务日志保留天数
    LOG_SECURITY_RETENTION_DAYS: int = 180   # 安全日志保留天数
    LOG_AUDIT_RETENTION_DAYS: int = 365     # 审计日志保留天数
    LOG_ROTATION_SIZE: str = "100 MB"        # 日志轮转大小，支持单位：KB, MB, GB
    LOG_COMPRESSION: str = "zip"             # 日志压缩格式：zip | gz | tar | tar.gz

    # ========== 安全配置 ==========
    SECRET_KEY: str = secrets.token_urlsafe(32)  # 应用密钥，用于JWT签名等，生产环境必须设置固定值
    JWT_ALGORITHM: str = "HS256"                 # JWT加密算法
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4    # 访问令牌过期时间（分钟），默认4小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # 刷新令牌过期时间（天），默认7天

    # ========== 数据库配置 ==========
    DB_ENGINE: str = "mysql"                     # 数据库引擎：sqlite | mysql | postgres

    # ========== MySQL 配置 ==========
    MYSQL_HOST: str = "localhost"                # MySQL服务器地址
    MYSQL_PORT: int = 3307                       # MySQL服务器端口
    MYSQL_USER: str = "app_user"                 # MySQL用户名
    MYSQL_PASSWORD: str = "123456"               # MySQL密码
    MYSQL_DATABASE: str = "app_db"               # MySQL数据库名称

    # ========== PostgreSQL 配置 ==========
    POSTGRES_HOST: str = "localhost"             # PostgreSQL服务器地址
    POSTGRES_PORT: int = 5432                    # PostgreSQL服务器端口
    POSTGRES_USER: str = "app_user"              # PostgreSQL用户名
    POSTGRES_PASSWORD: str = "123456"            # PostgreSQL密码
    POSTGRES_DB: str = "app_db"                  # PostgreSQL数据库名称

    # ========== Swagger 配置 ==========
    SWAGGER_UI_USERNAME: str = "admin"           # Swagger文档访问用户名
    SWAGGER_UI_PASSWORD: str = "qaz123456"       # Swagger文档访问密码，长度至少8位
    SUPER_ADMIN_PASSWORD: str = "qaz123456"      # 超级管理员初始密码

    # ========== Redis 配置 ==========
    REDIS_URL: str = "redis://:123456@localhost:6378/0"  # Redis连接URL，格式：redis://:password@host:port/db

    # ========== L1 本地缓存配置 ==========
    # L1缓存使用进程内存，适合高频访问的小数据，响应速度快但容量有限
    L1_CACHE_ENABLED: bool = True                # 是否启用L1本地缓存
    L1_CACHE_MAXSIZE: int = 1000                 # L1缓存最大条目数
    L1_CACHE_TTL_HIGH: int = 20                  # 高频数据TTL（秒）：用户会话、实时数据等
    L1_CACHE_TTL_MEDIUM: int = 40                # 中频数据TTL（秒）：字典数据、配置信息等
    L1_CACHE_TTL_LOW: int = 60                   # 低频数据TTL（秒）：系统配置、权限数据等

    # ========== L2 Redis 缓存配置 ==========
    # L2缓存使用Redis分布式存储，适合中低频访问的大数据，支持跨进程共享
    L2_CACHE_ENABLED: bool = True                # 是否启用L2 Redis缓存
    L2_CACHE_TTL_HIGH: int = 1800                # 高频数据TTL（秒）：用户会话、实时数据等（30分钟）
    L2_CACHE_TTL_MEDIUM: int = 21600             # 中频数据TTL（秒）：字典数据、配置信息等（6小时）
    L2_CACHE_TTL_LOW: int = 43200                # 低频数据TTL（秒）：系统配置、权限数据等（12小时）

    # ========== 缓存随机偏移配置（防止缓存雪崩）==========
    # 通过在TTL基础上添加随机偏移，避免大量缓存同时失效导致缓存雪崩
    CACHE_RANDOM_OFFSET_ENABLED: bool = True     # 是否启用随机TTL偏移
    L1_CACHE_RANDOM_OFFSET_PERCENT: int = 20     # L1缓存随机偏移百分比（0-100），实际TTL = TTL ± TTL*percent%
    L2_CACHE_RANDOM_OFFSET_PERCENT: int = 20     # L2缓存随机偏移百分比（0-100）

    # ========== 注册配置 ==========
    ALLOW_USER_REGISTRATION: bool = True         # 是否允许用户自主注册
    AUTO_LOGIN_AFTER_REGISTER: bool = True       # 注册后是否自动登录

    # ========== 调度器配置 ==========
    SCHEDULER_ENABLED: bool = True               # 是否启用调度器（定时任务）
    # 日志清理配置（天）
    SCHEDULER_LOGIN_LOG_RETENTION_DAYS: int = 90     # 登录日志保留天数
    SCHEDULER_OPERATION_LOG_RETENTION_DAYS: int = 180  # 操作日志保留天数
    # 软删除数据清理配置（天）
    SCHEDULER_SOFT_DELETE_RETENTION_DAYS: int = 30    # 软删除数据保留天数
    # Cron 表达式配置
    SCHEDULER_CLEAN_LOG_CRON: str = "0 2 * * *"      # 日志清理任务执行时间：每天凌晨2点
    SCHEDULER_CLEAN_SOFT_DELETE_CRON: str = "0 3 * * 0"  # 软删除清理任务执行时间：每周日凌晨3点

    # ========== 敏感词过滤配置 ==========
    ENABLE_SENSITIVE_WORD_FILTER: bool = False         # 是否启用敏感词过滤
    SENSITIVE_WORDS: list[str] = []                   # 敏感词列表
    SENSITIVE_WORD_RESPONSE: str = "内容包含敏感词，请修改后重试"  # 敏感词响应消息

    # ========== 其他配置 ==========
    DATETIME_FORMAT: str = DateTimeConst.FORMAT  # 日期时间格式，从constants.py引用
    COMPANY_ROLE_MAPPING: dict[str, list[int]] = {"default": []}  # 公司角色映射，key为公司ID，value为角色ID列表

    model_config = SettingsConfigDict(
        env_file=".env",                  # 环境变量文件路径
        env_file_encoding="utf-8",        # 文件编码格式
        case_sensitive=True,              # 配置项名称大小写敏感
        extra="ignore",                   # 忽略未定义的配置项
    )

    @field_validator("STORAGE_TYPE")
    @classmethod
    def validate_storage_type(cls, v):
        valid_types = ["local", "oss", "cos"]
        if v.lower() not in valid_types:
            raise ValueError(f"不支持的存储类型: {v}，支持的类型: {valid_types}")
        return v

    @field_validator("LOCAL_STORAGE_DIR")
    @classmethod
    def validate_local_storage_dir(cls, v):
        if not v:
            raise ValueError("本地存储目录不能为空")
        return v

    @field_validator("LOCAL_STORAGE_URL")
    @classmethod
    def validate_local_storage_url(cls, v):
        if not v:
            raise ValueError("本地存储URL不能为空")
        return v

    @property
    def BASE_DIR(self) -> str:
        """src目录路径（当前文件的祖父目录）"""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

    @property
    def PROJECT_ROOT(self) -> str:
        """项目根目录路径（src的父目录）"""
        return os.path.abspath(os.path.join(self.BASE_DIR, os.pardir))

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """将CORS_ORIGINS字符串转换为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """构建数据库连接URL
        """

        if self.DB_ENGINE == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        elif self.DB_ENGINE == "postgres":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"sqlite:///{self.PROJECT_ROOT}/db.sqlite3"

    @field_validator("COMPANY_ROLE_MAPPING", mode="before")
    @classmethod
    def parse_company_role_mapping(cls, v):
        """解析公司角色映射配置，支持JSON字符串格式"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"default": []}
        return v

    @field_validator("DB_ENGINE")
    @classmethod
    def validate_db_engine(cls, v):
        """验证数据库引擎类型"""
        valid_engines = ["sqlite", "mysql", "postgres", "postgresql"]
        if v.lower() not in valid_engines:
            raise ValueError(f"不支持的数据库引擎: {v}，支持的引擎: {valid_engines}")
        if v.lower() == "postgresql":
            return "postgres"
        return v.lower()

    @field_validator("MYSQL_PASSWORD", "POSTGRES_PASSWORD")
    @classmethod
    def validate_db_password(cls, v, info):
        """验证数据库密码，生产环境必须设置"""
        app_env = info.data.get("APP_ENV", "development")
        if not v and app_env == "production":
            raise ValueError("生产环境必须设置数据库密码")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        """验证SECRET_KEY长度，至少32字符"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度至少32字符")
        return v

    @field_validator("SWAGGER_UI_PASSWORD")
    @classmethod
    def validate_swagger_password(cls, v):
        """验证Swagger访问密码，长度至少6位"""
        if os.getenv("TESTING", "false").lower() == "true":
            return v or "test_password"
        if not v:
            raise ValueError("SWAGGER_UI_PASSWORD必须设置")
        if len(v) < 6:
            raise ValueError("Swagger访问密码长度至少6位")
        return v

    def __init__(self, **kwargs):
        """初始化配置，生产环境会执行额外的配置验证"""
        super().__init__(**kwargs)
        if self.APP_ENV == "production":
            self._validate_production_config()

    def _validate_production_config(self):
        """生产环境配置验证

        检查项：
        1. DEBUG模式必须关闭
        2. 不应使用SQLite数据库
        3. CORS不应允许localhost
        """
        if self.DEBUG:
            raise ValueError("生产环境不能启用DEBUG模式")

        if self.DB_ENGINE == "sqlite":
            raise ValueError("生产环境建议使用PostgreSQL或MySQL而非SQLite")

        if "localhost" in self.CORS_ORIGINS:
            raise ValueError("生产环境不应允许localhost的CORS访问")


# 全局配置实例
settings = Settings()
