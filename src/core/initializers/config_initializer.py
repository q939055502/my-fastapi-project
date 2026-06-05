"""
配置初始化器

负责系统配置项的初始化
"""

from sqlalchemy import func, select

from src.core.constants import StatusConst
from src.core.log import logger
from src.core.storage import get_db


def init_system_config():
    """
    初始化系统配置项

    创建系统级配置项，用于系统运行参数的统一管理
    """
    logger.info("开始初始化系统配置...")
    for session in get_db():
        from src.models.system import SystemConfig
        result = session.execute(select(SystemConfig))
        configs = result.scalars().first()
        if not configs:
            default_configs = [
                SystemConfig(
                    config_key="system.name",
                    config_value="房屋安全鉴定系统",
                    config_type="string",
                    remark="系统名称",
                    sort=1,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="system.version",
                    config_value="1.0.0",
                    config_type="string",
                    remark="系统版本",
                    sort=2,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="system.description",
                    config_value="业务APP + Web后端管理系统",
                    config_type="string",
                    remark="系统描述",
                    sort=3,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="login.max_fail_count",
                    config_value="5",
                    config_type="int",
                    remark="登录最大失败次数",
                    sort=4,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="login.lockout_duration",
                    config_value="30",
                    config_type="int",
                    remark="登录锁定时长(分钟)",
                    sort=5,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="register.enabled",
                    config_value="true",
                    config_type="bool",
                    remark="是否允许用户注册",
                    sort=6,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="captcha.enabled",
                    config_value="false",
                    config_type="bool",
                    remark="是否启用验证码",
                    sort=7,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="password.min_length",
                    config_value="6",
                    config_type="int",
                    remark="密码最小长度",
                    sort=8,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="password.require_uppercase",
                    config_value="false",
                    config_type="bool",
                    remark="密码是否需要大写字母",
                    sort=9,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="password.require_number",
                    config_value="false",
                    config_type="bool",
                    remark="密码是否需要数字",
                    sort=10,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="session.timeout_minutes",
                    config_value="120",
                    config_type="int",
                    remark="会话超时时间(分钟)",
                    sort=11,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                SystemConfig(
                    config_key="audit.log_retention_days",
                    config_value="90",
                    config_type="int",
                    remark="审计日志保留天数",
                    sort=12,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
            ]
            session.add_all(default_configs)
            session.commit()
            logger.info("系统配置初始化成功 - 配置项数量: 12")
        else:
            count_result = session.execute(select(func.count(SystemConfig.id)))
            config_count = count_result.scalar()
            logger.info(f"系统配置已存在，跳过初始化 - 当前配置数量: {config_count}")
        break
