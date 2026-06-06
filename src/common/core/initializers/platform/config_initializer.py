"""
配置初始化器

负责系统配置项的初始化
"""

from sqlalchemy import func, select
from src.common.core.constants import StatusConst
from src.common.core.log import logger
from src.common.core.storage import get_db


def init_system_config():
    """
    初始化系统配置项

    创建系统级配置项，用于系统运行参数的统一管理
    """
    logger.info("开始初始化系统配置...")
    for session in get_db():
        from src.models.platform import SystemConfig
        result = session.execute(select(SystemConfig))
        configs = result.scalars().first()
        if not configs:
            default_configs = [
                SystemConfig(
                    name="系统名称",
                    code="system.name",
                    value="房屋安全鉴定系统",
                    config_type="string",
                    group="system",
                    remark="系统名称",
                    sort=1,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="系统版本",
                    code="system.version",
                    value="1.0.0",
                    config_type="string",
                    group="system",
                    remark="系统版本",
                    sort=2,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="系统描述",
                    code="system.description",
                    value="业务APP + Web后端管理系统",
                    config_type="string",
                    group="system",
                    remark="系统描述",
                    sort=3,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="登录最大失败次数",
                    code="login.max_fail_count",
                    value="5",
                    config_type="int",
                    group="login",
                    remark="登录最大失败次数",
                    sort=4,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="登录锁定时长",
                    code="login.lockout_duration",
                    value="30",
                    config_type="int",
                    group="login",
                    remark="登录锁定时长(分钟)",
                    sort=5,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="是否允许注册",
                    code="register.enabled",
                    value="true",
                    config_type="boolean",
                    group="register",
                    remark="是否允许用户注册",
                    sort=6,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="是否启用验证码",
                    code="captcha.enabled",
                    value="false",
                    config_type="boolean",
                    group="captcha",
                    remark="是否启用验证码",
                    sort=7,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="密码最小长度",
                    code="password.min_length",
                    value="6",
                    config_type="int",
                    group="password",
                    remark="密码最小长度",
                    sort=8,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="会话超时时间",
                    code="session.timeout_minutes",
                    value="120",
                    config_type="int",
                    group="session",
                    remark="会话超时时间(分钟)",
                    sort=9,
                    status=StatusConst.ENABLED.value,
                ),
                SystemConfig(
                    name="审计日志保留天数",
                    code="audit.log_retention_days",
                    value="90",
                    config_type="int",
                    group="audit",
                    remark="审计日志保留天数",
                    sort=10,
                    status=StatusConst.ENABLED.value,
                ),
            ]
            session.add_all(default_configs)
            session.commit()
            logger.info("系统配置初始化成功 - 配置项数量: 10")
        else:
            count_result = session.execute(select(func.count(SystemConfig.id)))
            config_count = count_result.scalar()
            logger.info(f"系统配置已存在，跳过初始化 - 当前配置数量: {config_count}")
        break
