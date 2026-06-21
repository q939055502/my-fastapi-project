"""用户管理服务 - 管理员操作
此服务包含管理员对其他用户的操作:
- 用户列表查询
- 用户创建/更新/删除
- 用户详情查看
- 密码重置
"""

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError

from src.core.base.service_base import BaseService
from src.core.config import settings
from src.core.constants import RoleCodeConst
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage.cache.cache_manager import cache_manager, clear_user_cache
from src.core.storage.transaction_manager import TransactionManager
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.iam.rbac.repository.role_subject_repository import (
    role_subject_repository,
)
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.system.schemas.user import UserCreate, UserRoleItem, UserUpdate
from src.models.platform import AccountBind, User


class UserAdminService(BaseService):
    """用户管理服务 - 管理员操作"""

    def _check_system_role_assignment(self, role_uuids: list, session) -> None:
        """检查是否尝试分配系统内置角色"""
        if not role_uuids:
            return

        roles = session.execute(
            role_repository.model.__table__.select()
            .where(role_repository.model.uuid.in_(role_uuids))
        ).scalars().all()

        for role in roles:
            if role.is_system:
                raise BusinessException(
                    40300,
                    detail=f"禁止分配系统内置角色 '{role.name}'",
                )

    def _get_user_email(self, user_id: int, session) -> str | None:
        """获取用户的邮箱"""
        query = select(AccountBind).where(
            AccountBind.user_id == user_id,
            AccountBind.bind_type == 1,
            AccountBind.status == "verified",
            AccountBind.delete_time.is_(None)
        )
        result = session.execute(query).scalars().first()
        return result.identifier if result else None

    def _get_user_roles(self, user_id: int, session) -> list[UserRoleItem]:
        """获取用户角色列表"""
        role_ids = role_subject_repository.get_role_ids_by_subject(
            subject_id=user_id,
            subject_type=0,
            session=session
        )
        roles = role_repository.list_by_ids(role_ids=role_ids, session=session)
        return [
            UserRoleItem(
                uuid=role.uuid,
                name=role.name,
                remark=role.remark
            )
            for role in roles
        ]

    def get_user_list(
        self,
        page: int = 1,
        page_size: int = 10,
        username: str = "",
        email: str = "",
        org_uuid: str | None = None,
    ) -> tuple[int, list[User]]:
        """获取用户列表(管理员查询)"""
        with TransactionManager() as tm:
            search_filters = self._build_user_search_filters(
                username=username, email=email, org_uuid=org_uuid, session=tm.session
            )

            total, items = user_repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[desc(user_repository.model.created_at)],
            )

            return total, items

    @cache_manager.cached("user_detail", l1_ttl=settings.L1_CACHE_TTL_MEDIUM, l2_ttl=settings.L2_CACHE_TTL_MEDIUM)
    def get_user_detail(self, user_uuid: str) -> User:
        """获取用户详情(管理员查看)"""
        with TransactionManager() as tm:
            user_id = self.get_id_by_uuid("user", user_uuid, tm.session)
            if not user_id:
                raise BusinessException(40401, detail="用户不存在")

            user_obj = user_repository.get(id=user_id, session=tm.session)
            if not user_obj:
                raise BusinessException(40401, detail="用户不存在")

            return user_obj

    def create_user(self, user_in: UserCreate) -> User:
        """创建用户(管理员操作)"""
        logger.info(f"创建用户: {user_in.username}")

        with TransactionManager() as tm:
            existing_user_by_username = user_repository.get_by_username(user_in.username, session=tm.session)
            if existing_user_by_username:
                raise BusinessException(
                    40000,
                    detail=f"用户名 '{user_in.username}' 已存在",
                )

            existing_user_by_email = user_repository.get_by_email(user_in.email, session=tm.session)
            if existing_user_by_email:
                raise BusinessException(
                    40000,
                    detail=f"邮箱 '{user_in.email}' 已存在",
                )

            self._check_system_role_assignment(user_in.role_uuids, tm.session)

            try:
                new_user = user_repository.create_user(obj_in=user_in, session=tm.session)

                role_uuids_to_assign = user_in.role_uuids
                if not role_uuids_to_assign or len(role_uuids_to_assign) == 0:
                    from src.models.platform import Role
                    default_role = tm.session.execute(
                        Role.__table__.select().where(Role.code == RoleCodeConst.PLATFORM_NORMAL_USER.value)
                    ).first()
                    if default_role:
                        role_uuids_to_assign = [default_role.uuid]
                        logger.info(f"用户 {user_in.username} 自动分配默认角色: {RoleCodeConst.PLATFORM_NORMAL_USER.value}")

                # 获取当前用户ID作为创建者(管理员操作)
                from src.foundation.iam.auth.context import AuthContext
                creator_id = AuthContext.get_user_id()
                user_repository.update_roles(new_user.id, role_uuids_to_assign, creator_id, session=tm.session)

                tm.commit()

                logger.info(f"用户创建成功: {user_in.username}")
                return new_user
            except IntegrityError as e:
                tm.rollback()
                logger.error(f"用户创建失败: {user_in.username}, 错误: {e}")
                raise BusinessException(
                    40000,
                    detail="用户创建失败,可能用户名或邮箱已存在",
                ) from e

    def update_user(self, user_uuid: str, user_in: UserUpdate) -> None:
        """更新用户(管理员操作)"""
        logger.info(f"更新用户: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user_id = self.get_id_by_uuid("user", user_uuid, tm.session)
            if not user_id:
                raise BusinessException(40401, detail="用户不存在")

            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(40401, detail="用户不存在")

            if user_in.username and user_in.username != user.username:
                existing_user = user_repository.get_by_username(user_in.username, session=tm.session)
                if existing_user:
                    raise BusinessException(
                        40000,
                        detail=f"用户名 '{user_in.username}' 已存在",
                    )

            if user_in.email:
                # 查询用户当前的邮箱绑定
                current_email = self._get_user_email(user.id, tm.session)
                if current_email != user_in.email:
                    existing_user = user_repository.get_by_email(user_in.email, session=tm.session)
                    if existing_user and existing_user.id != user.id:
                        raise BusinessException(
                            40000,
                            detail=f"邮箱 '{user_in.email}' 已存在",
                        )

            user_repository.update(id=user.id, obj_in=user_in, session=tm.session)

            self._check_system_role_assignment(user_in.role_uuids, tm.session)

            if user_in.role_uuids is not None:
                if len(user_in.role_uuids) == 0:
                    raise BusinessException(
                        40000,
                        detail="用户必须至少绑定一个角色",
                    )

                # 获取当前用户ID作为创建者(管理员操作)
                from src.foundation.iam.auth.context import AuthContext
                creator_id = AuthContext.get_user_id()
                user_repository.update_roles(user.id, user_in.role_uuids, creator_id, session=tm.session)

            tm.commit()

        clear_user_cache(user.id)
        logger.info(f"用户更新成功: user_uuid={user_uuid}")

    def delete_user(self, user_uuid: str) -> None:
        """删除用户(管理员操作)"""
        logger.info(f"删除用户: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user_id = self.get_id_by_uuid("user", user_uuid, tm.session)
            if not user_id:
                raise BusinessException(40401, detail="用户不存在")

            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(40401, detail="用户不存在")

            user_repository.delete(id=user.id, session=tm.session)

            tm.commit()

        clear_user_cache(user.id)
        logger.info(f"用户删除成功: user_uuid={user_uuid}")

    def reset_user_password(self, user_uuid: str) -> str:
        """重置用户密码(管理员操作)"""
        logger.info(f"重置用户密码: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user_id = self.get_id_by_uuid("user", user_uuid, tm.session)
            if not user_id:
                raise BusinessException(40401, detail="用户不存在")

            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(40401, detail="用户不存在")

            result = user_repository.reset_password(user.id, session=tm.session)
            tm.commit()

        logger.info(f"用户密码重置成功: user_uuid={user_uuid}")
        return result

    def _build_user_search_filters(
        self,
        username: str = "",
        email: str = "",
        org_uuid: str | None = None,
        session=None,
    ) -> list:
        """构建用户搜索过滤条件"""
        filters = []

        if username:
            filters.append(user_repository.model.username.contains(username))

        # TODO: 需要实现按组织筛选用户的逻辑(通过 OrgClosure 或其他关联表�?        # org_uuid 参数暂时不处理,等待后续实现

        return filters


user_admin_service = UserAdminService()
