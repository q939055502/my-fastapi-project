"""
应用配置模块

使用 Pydantic V2 语法定义应用的配置项，支持从环境变量和 .env 文件读取配置。
包含应用的基本信息、CORS 配置、数据库配置、JWT 配置等。

职责划分：
- config.py: 应用配置（支持环境变量覆盖，从 constants.py 引用默认值）
- constants.py: 程序固定常量（真正固定不变的值）
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
    VERSION: str = "1.0.0"
    APP_TITLE: str = "管理系统"
    PROJECT_NAME: str = "管理系统"
    APP_DESCRIPTION: str = "业务APP + Web后端管理系统"

    APP_ENV: str = "production"
    DEBUG: bool = False

    # ========== 存储配置 ==========
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage"
    LOCAL_STORAGE_URL: str = "http://localhost:8000/storage"

    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
    OSS_BUCKET_NAME: str = ""

    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET_NAME: str = ""

    # ========== CORS 配置 ==========
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["Content-Type", "Authorization", "X-Requested-With"]

    # ========== 路径配置 ==========
    LOG_DIR: str = "./logs"

    # ========== 日志配置 ==========
    LOG_ACCESS_RETENTION_DAYS: int = 30      # 访问日志保留天数
    LOG_ERROR_RETENTION_DAYS: int = 90       # 错误日志保留天数
    LOG_BUSINESS_RETENTION_DAYS: int = 30    # 业务日志保留天数
    LOG_SECURITY_RETENTION_DAYS: int = 180   # 安全日志保留天数
    LOG_AUDIT_RETENTION_DAYS: int = 365     # 审计日志保留天数
    LOG_ROTATION_SIZE: str = "100 MB"        # 日志轮转大小
    LOG_COMPRESSION: str = "zip"             # 日志压缩格式

    # ========== 安全配置 ==========
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4    # 4小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # 7天

    # ========== 数据库配置 ==========
    DATABASE_URL: str = ""
    DB_ENGINE: str = "mysql" # 数据库引擎，可选值: postgres, mysql, sqlite

    # ========== MySQL 配置 ==========
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3307
    MYSQL_USER: str = "app_user"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "app_db"

    # ========== PostgreSQL 配置 ==========
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "app_db"

    # ========== Swagger 配置 ==========
    SWAGGER_UI_USERNAME: str = "admin"
    SWAGGER_UI_PASSWORD: str = "qaz123456"
    SUPER_ADMIN_PASSWORD: str = "qaz123456"

    # ========== Redis 配置 ==========
    REDIS_URL: str = "redis://:123456@localhost:6378/0"
    CACHE_TTL: int = 300    # 默认缓存时间（秒）

    # ========== L1 本地缓存配置 ==========
    L1_CACHE_ENABLED: bool = True
    L1_CACHE_MAXSIZE: int = 1000
    L1_CACHE_TTL: int = 300  # 5分钟

    # ========== 注册配置 ==========
    ALLOW_USER_REGISTRATION: bool = True
    AUTO_LOGIN_AFTER_REGISTER: bool = True

    # ========== 调度器配置 ==========
    SCHEDULER_ENABLED: bool = True
    # 日志清理配置（天）
    SCHEDULER_LOGIN_LOG_RETENTION_DAYS: int = 90
    SCHEDULER_OPERATION_LOG_RETENTION_DAYS: int = 180
    # 软删除数据清理配置（天）
    SCHEDULER_SOFT_DELETE_RETENTION_DAYS: int = 30
    # Cron 表达式配置
    SCHEDULER_CLEAN_LOG_CRON: str = "0 2 * * *"      # 每天凌晨2点执行
    SCHEDULER_CLEAN_SOFT_DELETE_CRON: str = "0 3 * * 0"  # 每周日凌晨3点执行

    # ========== 其他配置 ==========
    DATETIME_FORMAT: str = DateTimeConst.FORMAT
    COMPANY_ROLE_MAPPING: dict[str, list[int]] = {"default": []}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
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
    def PROJECT_ROOT(self) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    @property
    def BASE_DIR(self) -> str:
        return os.path.abspath(os.path.join(self.PROJECT_ROOT, os.pardir))

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_ENGINE == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        elif self.DB_ENGINE == "postgres":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"sqlite:///{self.BASE_DIR}/db.sqlite3"

    @field_validator("COMPANY_ROLE_MAPPING", mode="before")
    @classmethod
    def parse_company_role_mapping(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"default": []}
        return v

    @field_validator("DB_ENGINE")
    @classmethod
    def validate_db_engine(cls, v):
        valid_engines = ["sqlite", "mysql", "postgres", "postgresql"]
        if v.lower() not in valid_engines:
            raise ValueError(f"不支持的数据库引擎: {v}，支持的引擎: {valid_engines}")
        if v.lower() == "postgresql":
            return "postgres"
        return v.lower()

    @field_validator("MYSQL_PASSWORD", "POSTGRES_PASSWORD")
    @classmethod
    def validate_db_password(cls, v, info):
        app_env = info.data.get("APP_ENV", "development")
        if not v and app_env == "production":
            raise ValueError("生产环境必须设置数据库密码")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度至少32字符")
        return v

    @field_validator("SWAGGER_UI_PASSWORD")
    @classmethod
    def validate_swagger_password(cls, v):
        if os.getenv("TESTING", "false").lower() == "true":
            return v or "test_password"
        if not v:
            raise ValueError("SWAGGER_UI_PASSWORD必须设置")
        if len(v) < 8:
            raise ValueError("Swagger访问密码长度至少8位")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.APP_ENV == "production":
            self._validate_production_config()

    def _validate_production_config(self):
        if self.DEBUG:
            raise ValueError("生产环境不能启用DEBUG模式")

        if self.DB_ENGINE == "sqlite":
            raise ValueError("生产环境建议使用PostgreSQL或MySQL而非SQLite")

        if "localhost" in self.CORS_ORIGINS:
            raise ValueError("生产环境不应允许localhost的CORS访问")


settings = Settings()
