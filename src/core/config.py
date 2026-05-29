# 读取 .env，做封装 / 校验 / 类型转换，
import json
import os
import secrets

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

"""
应用配置模块

使用 Pydantic V2 语法定义应用的配置项，支持从环境变量和 .env 文件读取配置。
包含应用的基本信息、CORS 配置、数据库配置、JWT 配置等。
"""


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

    APP_ENV: str = "development"
    DEBUG: bool = True

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

    # ========== 安全配置 ==========
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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
    CACHE_TTL: int = 300

    # ========== 其他配置 ==========
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
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
        """验证存储类型

        Args:
            v: 存储类型值

        Returns:
            str: 验证后的存储类型

        Raises:
            ValueError: 存储类型不支持时抛出
        """
        valid_types = ["local", "oss", "cos"]
        if v.lower() not in valid_types:
            raise ValueError(f"不支持的存储类型: {v}，支持的类型: {valid_types}")
        return v

    @field_validator("LOCAL_STORAGE_DIR")
    @classmethod
    def validate_local_storage_dir(cls, v):
        """验证本地存储目录

        Args:
            v: 本地存储目录路径

        Returns:
            str: 验证后的目录路径
        """
        if not v:
            raise ValueError("本地存储目录不能为空")
        return v

    @field_validator("LOCAL_STORAGE_URL")
    @classmethod
    def validate_local_storage_url(cls, v):
        """验证本地存储URL

        Args:
            v: 本地存储URL

        Returns:
            str: 验证后的URL
        """
        if not v:
            raise ValueError("本地存储URL不能为空")
        return v

    @property
    def PROJECT_ROOT(self) -> str:
        """项目根目录"""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    @property
    def BASE_DIR(self) -> str:
        """应用基础目录"""
        return os.path.abspath(os.path.join(self.PROJECT_ROOT, os.pardir))

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """将CORS_ORIGINS字符串转换为列表

        Returns:
            list[str]: CORS 来源列表
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """生成 SQLAlchemy 数据库连接 URL

        Returns:
            str: 数据库连接 URL
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_ENGINE == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        elif self.DB_ENGINE == "postgres":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:  # sqlite 作为备用
            return f"sqlite:///{self.BASE_DIR}/db.sqlite3"

    @field_validator("COMPANY_ROLE_MAPPING", mode="before")
    @classmethod
    def parse_company_role_mapping(cls, v):
        """解析 COMPANY_ROLE_MAPPING 环境变量

        Args:
            v: 环境变量值

        Returns:
            dict[str, list[int]]: 解析后的公司角色映射
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"default": []}
        return v

    @field_validator("DB_ENGINE")
    @classmethod
    def validate_db_engine(cls, v):
        """验证数据库引擎

        Args:
            v: 数据库引擎值

        Returns:
            str: 验证后的数据库引擎

        Raises:
            ValueError: 数据库引擎不支持时抛出
        """
        valid_engines = ["sqlite", "mysql", "postgres", "postgresql"]
        if v.lower() not in valid_engines:
            raise ValueError(f"不支持的数据库引擎: {v}，支持的引擎: {valid_engines}")
        # 统一别名，postgres 和 postgresql 都使用 postgres
        if v.lower() == "postgresql":
            return "postgres"
        return v.lower()

    @field_validator("MYSQL_PASSWORD", "POSTGRES_PASSWORD")
    @classmethod
    def validate_db_password(cls, v, info):
        """验证数据库密码

        Args:
            v: 密码值
            info: 验证信息

        Returns:
            str: 验证后的密码

        Raises:
            ValueError: 生产环境密码为空时抛出
        """
        app_env = info.data.get("APP_ENV", "development")
        if not v and app_env == "production":
            raise ValueError("生产环境必须设置数据库密码")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        """验证SECRET_KEY强度

        Args:
            v: 密钥值

        Returns:
            str: 验证后的密钥

        Raises:
            ValueError: 密钥长度不足时抛出
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度至少32字符")
        return v

    @field_validator("SWAGGER_UI_PASSWORD")
    @classmethod
    def validate_swagger_password(cls, v):
        """验证Swagger访问密码

        Args:
            v: 密码值

        Returns:
            str: 验证后的密码

        Raises:
            ValueError: 密码为空或长度不足时抛出
        """
        if os.getenv("TESTING", "false").lower() == "true":
            return v or "test_password"
        if not v:
            raise ValueError("SWAGGER_UI_PASSWORD必须设置")
        if len(v) < 8:
            raise ValueError("Swagger访问密码长度至少8位")
        return v

    def __init__(self, **kwargs):
        """初始化配置

        Args:
            **kwargs: 配置参数
        """
        super().__init__(**kwargs)
        if self.APP_ENV == "production":
            self._validate_production_config()

    def _validate_production_config(self):
        """生产环境特定配置验证

        Raises:
            ValueError: 生产环境配置不符合要求时抛出
        """
        if self.DEBUG:
            raise ValueError("生产环境不能启用DEBUG模式")

        if self.DB_ENGINE == "sqlite":
            raise ValueError("生产环境建议使用PostgreSQL或MySQL而非SQLite")

        if "localhost" in self.CORS_ORIGINS:
            raise ValueError("生产环境不应允许localhost的CORS访问")


settings = Settings()

