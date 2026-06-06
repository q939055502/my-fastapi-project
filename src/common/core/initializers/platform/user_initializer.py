"""
用户初始化器

负责超级管理员和测试用户的创建
"""

from sqlalchemy import select
from src.common.core.config import settings
from src.common.core.log import logger
from src.common.core.storage import get_db


def init_superuser():
    """
    初始化超级管理员用户和普通测试用户

    检查是否已存在超级管理员用户，若不存在则创建默认超级管理员：
    - 用户名: superadmin
    - 邮箱: superadmin@superadmin.com
    - 密码: qaz123456

    同时创建普通测试用户：
    - 用户名: user1
    - 邮箱: user1@example.com
    - 密码: qaz123456

    - 用户名: user2
    - 邮箱: user2@example.com
    - 密码: qaz123456

    权限通过角色来管理，不再使用is_superuser字段
    """
    logger.info("开始初始化超级管理员用户...")
    for session in get_db():
        try:
            from src.modules.platform.repository.user_repository import (
                UserCreate,
                user_repository,
            )

            result = session.execute(select(user_repository.model))
            user = result.scalars().first()
            if not user:
                user_repository.create_user(
                    UserCreate(
                        username="superadmin",
                        email="superadmin@superadmin.com",
                        password=settings.SUPER_ADMIN_PASSWORD,
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("超级管理员用户创建成功 - 用户名: superadmin")
            else:
                logger.info("超级管理员用户已存在，跳过创建")

            user1_result = session.execute(
                select(user_repository.model).where(user_repository.model.username == "user1")
            )
            user1 = user1_result.scalars().first()
            if not user1:
                user_repository.create_user(
                    UserCreate(
                        username="user1",
                        email="user1@example.com",
                        password="qaz123456",
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("普通测试用户创建成功 - 用户名: user1")
            else:
                logger.info("普通测试用户已存在，跳过创建")

            user2_result = session.execute(
                select(user_repository.model).where(user_repository.model.username == "user2")
            )
            user2 = user2_result.scalars().first()
            if not user2:
                user_repository.create_user(
                    UserCreate(
                        username="user2",
                        email="user2@example.com",
                        password="qaz123456",
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("普通测试用户创建成功 - 用户名: user2")
            else:
                logger.info("普通测试用户已存在，跳过创建")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化用户失败: {str(e)}")
            raise
        break
