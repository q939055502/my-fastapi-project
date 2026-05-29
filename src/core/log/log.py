import os
import sys

from loguru import logger as loguru_logger

from src.core.config import settings


class LoggingConfig:
    """统一日志配置管理 - 支持多租户和日志分类"""

    def __init__(self) -> None:
        self.debug = settings.DEBUG
        self.level = "DEBUG" if self.debug else "INFO"
        self.log_dir = settings.LOG_DIR
        self._ensure_log_dirs()

    def _ensure_log_dirs(self):
        """确保所有日志分类目录存在"""
        log_categories = ["access", "error", "business", "security", "audit"]
        for category in log_categories:
            category_dir = os.path.join(self.log_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir, exist_ok=True)

    def get_log_format(self):
        """获取统一的日志格式（含tenant_id）"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<blue>{extra[tenant_id]: <12}</blue> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    def get_file_format(self):
        """获取文件日志格式（无颜色）"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{extra[tenant_id]: <12} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

    def _get_access_filter(self, record):
        """访问日志过滤器 - 只记录HTTP 请求相关"""
        return "core.middlewares" in record["name"]

    def _get_error_filter(self, record):
        """错误日志过滤器 - 只记录ERROR 及以上级别"""
        return record["level"].no >= 40

    def _get_business_filter(self, record):
        """业务日志过滤器 - 只记录业务服务相关"""
        module = record["name"]
        # 业务服务模块
        if "services." in module:
            return True
        # API 层业务接口
        if "api.v1." in module and any(keyword in module for keyword in ["users", "roles", "depts", "tenant", "resource", "plans"]):
            return True
        return False

    def _get_security_filter(self, record):
        """安全日志过滤器 - 只记录安全认证相关"""
        module = record["name"]
        message = record["message"].lower()
        # 安全认证模块
        if any(keyword in module for keyword in ["dependency", "security", "token_manager"]):
            return True
        # 登录、登出、认证相关
        if any(keyword in message for keyword in ["认证", "登录", "logout", "login", "token", "令牌", "权限"]):
            return True
        return False

    def _get_audit_filter(self, record):
        """审计日志过滤器 - 只记录审计相关"""
        module = record["name"]
        message = record["message"].lower()
        # 审计相关模块或关键词
        if "audit" in module.lower():
            return True
        if any(keyword in message for keyword in ["审计", "audit", "创建", "删除", "更新", "create", "delete", "update"]):
            return True
        return False

    def setup_logger(self):
        """配置日志输出"""
        # 清除默认处理器
        loguru_logger.remove()

        # 创建带默认tenant_id 的logger
        logger_with_tenant = loguru_logger.bind(tenant_id="system")

        # 控制台输出（带颜色）- 所有日志
        logger_with_tenant.add(
            sink=sys.stdout,
            level=self.level,
            format=self.get_log_format(),
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

        # ========== 日志分类输出 ==========

        # 1. 访问日志 - HTTP 请求日志
        logger_with_tenant.add(
            sink=f"{self.log_dir}/access/access_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format=self.get_file_format(),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=False,
            diagnose=False,
            filter=self._get_access_filter,
        )

        # 2. 错误日志 - ERROR 及以上级别
        logger_with_tenant.add(
            sink=f"{self.log_dir}/error/error_{{time:YYYY-MM-DD}}.log",
            level="ERROR",
            format=self.get_file_format(),
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
            filter=self._get_error_filter,
        )

        # 3. 业务日志 - 业务服务相关
        logger_with_tenant.add(
            sink=f"{self.log_dir}/business/business_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format=self.get_file_format(),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
            filter=self._get_business_filter,
        )

        # 4. 安全日志 - 安全认证相关
        logger_with_tenant.add(
            sink=f"{self.log_dir}/security/security_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format=self.get_file_format(),
            rotation="100 MB",
            retention="180 days",
            compression="zip",
            encoding="utf-8",
            backtrace=False,
            diagnose=False,
            filter=self._get_security_filter,
        )

        # 5. 审计日志 - 审计相关
        logger_with_tenant.add(
            sink=f"{self.log_dir}/audit/audit_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format=self.get_file_format(),
            rotation="100 MB",
            retention="365 days",
            compression="zip",
            encoding="utf-8",
            backtrace=False,
            diagnose=False,
            filter=self._get_audit_filter,
        )

        # 记录日志系统启动
        logger_with_tenant.info("日志系统已启动")

        return logger_with_tenant


# 全局日志配置实例
logging_config = LoggingConfig()
logger = logging_config.setup_logger()


def get_logger(tenant_id: int | None = None) -> loguru_logger.__class__:
    """获取带租户ID的日志实例
    Args:
        tenant_id: 租户ID，默认为 system（系统级操作）
    Returns:
        绑定了tenant_id 的logger 实例
    """
    tenant = tenant_id if tenant_id else "system"
    return logger.bind(tenant_id=tenant)
