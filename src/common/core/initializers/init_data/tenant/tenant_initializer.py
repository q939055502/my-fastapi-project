"""
租户初始化器

负责租户套餐和默认租户的创建
"""

from sqlalchemy import func, select
from src.common.core.constants import StatusConst
from src.common.core.log import logger
from src.common.core.storage import get_db


def init_plans():
    """
    初始化租户套餐

    创建默认的租户套餐：
    - 免费版（自动通过，限5个用户）
    - 基础版（自动通过，限20个用户）
    - 专业版（人工审核，限100个用户）
    - 企业版（人工审核，无用户限制）
    """
    logger.info("开始初始化租户套餐...")
    for session in get_db():
        from src.models.platform import TenantPlan
        result = session.execute(select(TenantPlan))
        plans = result.scalars().first()
        if not plans:
            default_plans = [
                TenantPlan(
                    name="免费版",
                    code="free",
                    is_auto_approve=1,
                    max_users=5,
                    max_depts=3,
                    max_storage=1024,
                    max_file_size=10,
                    price_year=0,
                    available_features="基础功能",
                    available_modules="user,dept",
                    status=StatusConst.ENABLED,
                    sort=1
                ),
                TenantPlan(
                    name="基础版",
                    code="basic",
                    is_auto_approve=1,
                    max_users=20,
                    max_depts=10,
                    max_storage=10240,
                    max_file_size=50,
                    price_year=9900,
                    available_features="标准功能",
                    available_modules="user,dept,dict",
                    status=StatusConst.ENABLED,
                    sort=2
                ),
                TenantPlan(
                    name="专业版",
                    code="professional",
                    is_auto_approve=0,
                    max_users=100,
                    max_depts=50,
                    max_storage=102400,
                    max_file_size=100,
                    price_year=29900,
                    available_features="高级功能",
                    available_modules="user,dept,dict,file",
                    status=StatusConst.ENABLED,
                    sort=3
                ),
                TenantPlan(
                    name="企业版",
                    code="enterprise",
                    is_auto_approve=0,
                    max_users=None,
                    max_depts=None,
                    max_storage=1048576,
                    max_file_size=500,
                    price_year=99900,
                    available_features="企业级功能",
                    available_modules="user,dept,dict,file,log",
                    status=StatusConst.ENABLED,
                    sort=4
                ),
            ]
            session.add_all(default_plans)
            session.commit()
            logger.info("租户套餐初始化成功 - 套餐数量: 4")
        else:
            count_result = session.execute(select(func.count(TenantPlan.id)))
            plan_count = count_result.scalar()
            logger.info(f"租户套餐已存在，跳过初始化 - 当前套餐数量: {plan_count}")
        break


def init_default_tenant():
    """
    初始化默认租户

    创建一个默认业务租户，并将 user1 设为其户主：
    - 租户名称: 默认租户
    - 租户编码: default
    - 套餐: 免费版
    - 户主: user1
    """
    logger.info("开始初始化默认租户...")
    for session in get_db():
        try:
            from src.models.tenant import Tenant, TenantMember
            from src.foundation.platform.repository.user_repository import user_repository

            result = session.execute(select(Tenant).where(Tenant.code == "default"))
            default_tenant = result.scalars().first()

            if not default_tenant:
                user1_result = session.execute(
                    select(user_repository.model).where(user_repository.model.username == "user1")
                )
                user1 = user1_result.scalars().first()

                if user1:
                    default_tenant = Tenant(
                        name="默认租户",
                        code="default",
                        owner_user_id=user1.id,
                        status="active"
                    )
                    session.add(default_tenant)
                    session.flush()

                    tenant_member = TenantMember(
                        user_id=user1.id,
                        tenant_id=default_tenant.id,
                        subject_id=default_tenant.id,
                        is_owner=True
                    )
                    session.add(tenant_member)

                    session.commit()
                    logger.info(f"默认租户创建成功 - 租户ID: {default_tenant.id}, 户主: user1")
                else:
                    logger.warning("user1 用户不存在，跳过创建默认租户")
            else:
                logger.info("默认租户已存在，跳过创建")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化默认租户失败: {str(e)}")
            raise
        break
