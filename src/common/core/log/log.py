import os
import sys

from loguru import logger as loguru_logger
from src.common.core.config import settings


class LoggingConfig:
    """统一日志配置管理 - 支持多租户和日志分类"""

    def __init__(self) -> None:
        self.debug = settings.DEBUG
        self.level = "DEBUG" if self.debug else "INFO"
        self.log_dir = settings.LOG_DIR
        self._ensure_log_dirs()

    def _ensure_log_dirs(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def get_log_format(self):
        """获取统一的日志格式（带颜色，用于控制台）"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "      # 时间
            "<level>{level: <8}</level> | "                          # 级别
            "<yellow>{extra[request_id]: <36}</yellow> | "           # 请求ID
            "<blue>{extra[tenant_id]: <10}</blue> | "                # 租户ID
            "<magenta>{extra[user_id]: <8}</magenta> | "             # 用户ID
            "<cyan>{extra[ip]: <15}</cyan> | "                       # IP
            "<white>{extra[endpoint]: <30}</white> | "               # 接口
            "<green>{extra[duration]: <8}</green> | "                # 耗时
            "<red>{extra[business_code]: <8}</red> | "               # 业务码
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "  # 代码位置
            "<level>{message}</level>"                               # 日志信息
        )

    def get_file_format(self):
        """获取文件日志格式（无颜色）"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "          # 时间
            "{level: <8} | "                              # 级别
            "{extra[request_id]: <36} | "                  # 请求ID
            "{extra[tenant_id]: <10} | "                   # 租户ID
            "{extra[user_id]: <8} | "                      # 用户ID
            "{extra[ip]: <15} | "                          # IP
            "{extra[endpoint]: <30} | "                    # 接口
            "{extra[duration]: <8} | "                     # 耗时
            "{extra[business_code]: <8} | "                # 业务码
            "{name}:{function}:{line} | "                  # 代码位置（ERROR级别时显示）
            "{message}"                                    # 日志信息
        )



    def setup_logger(self):
        """配置日志输出"""
        # 清除默认处理器
        loguru_logger.remove()

        # 创建带所有字段默认值的 logger
        logger_with_tenant = loguru_logger.bind(
            request_id="-",
            tenant_id="system",
            user_id="0",
            ip="unknown",
            endpoint="-",
            duration="0ms",
            business_code="-",
        )

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

        # 统一文件日志 - 所有日志都输出到一个文件
        logger_with_tenant.add(
            sink=f"{self.log_dir}/app_{{time:YYYY-MM-DD}}.log",  # 日志输出路径，{time:YYYY-MM-DD}自动按日期生成文件名
            level="DEBUG",           # 日志级别：DEBUG及以上都记录
            format=self.get_file_format(),  # 日志格式（无颜色，便于文件存储）
            rotation=settings.LOG_ROTATION_SIZE,  # 日志轮转：文件达到指定大小后自动切割
            retention="30 days",     # 日志保留时间：超过30天的日志自动删除
            compression=settings.LOG_COMPRESSION,  # 压缩格式：轮转后的日志文件压缩格式（如zip）
            encoding="utf-8",        # 文件编码：确保中文正常显示
            backtrace=True,          # 回溯信息：异常时显示完整调用栈
            diagnose=True,           # 诊断信息：显示变量值等调试信息（仅DEBUG级别）
            enqueue=True,            # 异步写入：通过队列异步写入文件，不阻塞主线程
        )

        # 记录日志系统启动
        logger_with_tenant.info("日志系统已启动")

        return logger_with_tenant


# 全局日志配置实例
logging_config = LoggingConfig()
logger = logging_config.setup_logger()





def get_ctx_logger() -> loguru_logger.__class__:
    """获取带当前请求上下文的日志实例

    自动从 ContextVar 获取当前的日志上下文，并绑定到 logger 上。
    在 HTTP 请求中调用时，会自动包含 request_id、tenant_id、user_id 等信息。
    在非 HTTP 环境（如定时任务）中调用时，使用默认值。

    Returns:
        绑定了当前上下文的 logger 实例
    """
    from src.common.core.context.log_context import get_log_context

    ctx = get_log_context()
    return logger.bind(
        request_id=ctx.request_id,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        ip=ctx.ip,
        endpoint=ctx.endpoint,
        duration=ctx.duration,
        business_code=ctx.business_code,
    )
