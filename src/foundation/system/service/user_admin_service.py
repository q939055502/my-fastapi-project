"""用户管理服务 - 管理员操作

此服务包含管理员对其他用户的操作：
- 用户列表查询
- 用户创建/更新/删除
- 用户详情查看
- 密码重置
"""

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from src.core.config import settings
from src.core.constants import RoleCodeConst
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage.cache.cache_manager import cache_manager, clear_user_cache
from src.core.storage.transaction_manager import TransactionManager
from src.foundation.system.repository.org_repository import org_repository
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.iam.rbac.repository.role_subject_repository import (
    role_subject_repository,
)
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.system.schemas.user import UserCreate, UserUpdate
from src.models.platform import AccountBind


class UserAdminService:
    """用户管理服务 - 管理员操作"""

    def _check_system_role_assignment(self, role_uuids: list[UUID], session) -> None:
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
                    ResponseCode.FORBIDDEN,
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

    def _user_to_dict(self, user_obj, include_roles: bool = True, roles: list = None, session = None) -> dict:
        """将用户对象转换为字典，排除密码字段

        Args:
            user_obj: 用户对象
            include_roles: 是否包含角色信息
            roles: 角色列表（通过 role_subject_repository 查询得到）
            session: 数据库会话（用于查询 AccountBind）
        """
        user_dict = user_obj.to_dict(exclude_fields=["password", "id"])

        # 添加 email 字段，从 AccountBind 中查询
        if session:
            email = self._get_user_email(user_obj.id, session)
            if email:
                user_dict["email"] = email

        if include_roles and roles:
            user_dict["roles"] = [
                {
                    "uuid": role.uuid,
                    "name": role.name,
                    "remark": role.remark
                }
                for role in roles
            ]

        return user_dict

    def get_user_list(
        self,
        page: int = 1,
        page_size: int = 10,
        username: str = "",
        email: str = "",
        org_uuid: UUID | None = None,
    ) -> tuple[int, list[dict]]:
        """获取用户列表（管理员）"""
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

            data = self._transform_user_list(items, tm.session)

            return total, data

    @cache_manager.cached("user_detail", l1_ttl=settings.L1_CACHE_TTL_MEDIUM, l2_ttl=settings.L2_CACHE_TTL_MEDIUM)
    def get_user_detail(self, user_uuid: UUID) -> dict:
        """获取用户详情（管理员查看）"""
        with TransactionManager() as tm:
            user_obj = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户不存在")

            roles = role_subject_repository.get_roles_by_subject(
                subject_id=user_obj.id,
                subject_type=0,
                session=tm.session
            )

            return self._user_to_dict(user_obj, include_roles=True, roles=roles, session=tm.session)

    def create_user(self, user_in: UserCreate) -> dict:
        """创建用户（管理员）"""
        logger.info(f"创建用户: {user_in.username}")

        with TransactionManager() as tm:
            existing_user_by_username = user_repository.get_by_username(user_in.username, session=tm.session)
            if existing_user_by_username:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail=f"用户名 '{user_in.username}' 已存在",
                )

            existing_user_by_email = user_repository.get_by_email(user_in.email, session=tm.session)
            if existing_user_by_email:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
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

                # 获取当前用户ID作为创建者（管理员操作）
                from src.foundation.iam.auth.context import AuthContext
                creator_id = AuthContext.get_user_id()
                user_repository.update_roles(new_user.id, role_uuids_to_assign, creator_id, session=tm.session)

                tm.commit()

                roles = role_subject_repository.get_roles_by_subject(
                    subject_id=new_user.id,
                    subject_type=0,
                    session=tm.session
                )
                result = self._user_to_dict(new_user, include_roles=True, roles=roles, session=tm.session)
                logger.info(f"用户创建成功: {user_in.username}")
                return result
            except IntegrityError as e:
                tm.rollback()
                logger.error(f"用户创建失败: {user_in.username}, 错误: {e}")
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail="用户创建失败，可能用户名或邮箱已存在",
                ) from e

    def update_user(self, user_uuid: UUID, user_in: UserUpdate) -> None:
        """更新用户（管理员）"""
        logger.info(f"更新用户: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户不存在")

            if user_in.username and user_in.username != user.username:
                existing_user = user_repository.get_by_username(user_in.username, session=tm.session)
                if existing_user:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail=f"用户名 '{user_in.username}' 已存在",
                    )

            if user_in.email:
                # 查询用户当前的邮箱绑定
                current_email = self._get_user_email(user.id, tm.session)
                if current_email != user_in.email:
                    existing_user = user_repository.get_by_email(user_in.email, session=tm.session)
                    if existing_user and existing_user.id != user.id:
                        raise BusinessException(
                            ResponseCode.PARAM_ERROR,
                            detail=f"邮箱 '{user_in.email}' 已存在",
                        )

            user_repository.update(id=user.id, obj_in=user_in, session=tm.session)

            self._check_system_role_assignment(user_in.role_uuids, tm.session)

            if user_in.role_uuids is not None:
                if len(user_in.role_uuids) == 0:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail="用户必须至少绑定一个角色",
                    )

                # 获取当前用户ID作为创建者（管理员操作）
                from src.foundation.iam.auth.context import AuthContext
                creator_id = AuthContext.get_user_id()
                user_repository.update_roles(user.id, user_in.role_uuids, creator_id, session=tm.session)

            tm.commit()

        clear_user_cache(user.id)
        logger.info(f"用户更新成功: user_uuid={user_uuid}")

    def delete_user(self, user_uuid: UUID) -> None:
        """删除用户（管理员）"""
        logger.info(f"删除用户: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户不存在")

            success = user_repository.delete(id=user.id, session=tm.session)

            tm.commit()

        clear_user_cache(user.id)
        logger.info(f"用户删除成功: user_uuid={user_uuid}")

    def reset_user_password(self, user_uuid: UUID) -> str:
        """重置用户密码（管理员）"""
        logger.info(f"重置用户密码: user_uuid={user_uuid}")

        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户不存在")

            result = user_repository.reset_password(user.id, session=tm.session)
            tm.commit()

        logger.info(f"用户密码重置成功: user_uuid={user_uuid}")
        return result

    def _build_user_search_filters(
        self,
        username: str = "",
        email: str = "",
        org_uuid: UUID | None = None,
        session=None,
    ) -> list:
        """构建用户搜索过滤条件"""
        filters = []

        if username:
            filters.append(user_repository.model.username.contains(username))

        # TODO: 需要实现按组织筛选用户的逻辑（通过 OrgClosure 或其他关联表）
        # org_uuid 参数暂时不处理，等待后续实现

        return filters

    def _transform_user_list(self, items, session) -> list[dict]:
        """转换用户列表，添加角色信息"""
        data = []

        for obj in items:
            roles = role_subject_repository.get_roles_by_subject(
                subject_id=obj.id,
                subject_type=0,
                session=session
            )
            user_dict = self._user_to_dict(obj, include_roles=True, roles=roles, session=session)

            data.append(user_dict)

        return data


user_admin_service = UserAdminService()