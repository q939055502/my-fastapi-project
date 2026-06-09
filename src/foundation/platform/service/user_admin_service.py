"""用户管理服务 - 管理员操作

此服务包含管理员对其他用户的操作：
- 用户列表查询
- 用户创建/更新/删除
- 用户详情查看
- 密码重置
"""

from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from src.common.core.config import settings
from src.common.core.constants import RoleCodeConst
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.log import logger
from src.common.core.storage.cache.cache_manager import cache_manager, clear_user_cache
from src.common.core.storage.transaction_manager import TransactionManager
from src.foundation.platform.repository.dept_repository import dept_repository
from src.foundation.platform.repository.role_repository import role_repository
from src.foundation.platform.repository.role_subject_repository import (
    role_subject_repository,
)
from src.foundation.platform.repository.user_repository import user_repository
from src.foundation.platform.schemas.user import UserCreate, UserUpdate


class UserAdminService:
    """用户管理服务 - 管理员操作"""

    def _check_system_role_assignment(self, role_ids: list[int], session) -> None:
        """检查是否尝试分配系统内置角色"""
        if not role_ids:
            return

        roles = session.execute(
            role_repository.model.__table__.select()
            .where(role_repository.model.id.in_(role_ids))
        ).scalars().all()

        for role in roles:
            if role.is_system:
                raise BusinessException(
                    ResponseCode.FORBIDDEN,
                    detail=f"禁止分配系统内置角色 '{role.name}'",
                )

    def _user_to_dict(self, user_obj, include_roles: bool = True, roles: list = None) -> dict:
        """将用户对象转换为字典，排除密码字段

        Args:
            user_obj: 用户对象
            include_roles: 是否包含角色信息
            roles: 角色列表（通过 role_subject_repository 查询得到）
        """
        user_dict = user_obj.to_dict(exclude_fields=["password"])

        # 添加 email 字段，从 AccountBind 中获取
        if hasattr(user_obj, "account_binds"):
            for bind in user_obj.account_binds:
                if bind.bind_type == 1 and bind.status == "verified":
                    user_dict["email"] = bind.identifier
                    break

        if include_roles and roles:
            user_dict["roles"] = [
                {
                    "id": role.id,
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
        dept_id: int | None = None,
    ) -> tuple[int, list[dict]]:
        """获取用户列表（管理员）"""
        with TransactionManager() as tm:
            search_filters = self._build_user_search_filters(
                username=username, email=email, dept_id=dept_id
            )

            total, items = user_repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[desc(user_repository.model.created_at)],
            )

            data = self._transform_user_list_with_dept(items, tm.session)

            return total, data

    @cache_manager.cached("user_detail", l1_ttl=settings.L1_CACHE_TTL_MEDIUM, l2_ttl=settings.L2_CACHE_TTL_MEDIUM)
    def get_user_detail(self, user_id: int) -> dict:
        """获取用户详情（管理员查看）"""
        with TransactionManager() as tm:
            user_obj = user_repository.get(id=user_id, session=tm.session)
            if not user_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户ID: {user_id} 不存在")

            # 通过 role_subject_repository 获取用户角色（subject_type=0 表示平台用户）
            roles = role_subject_repository.get_roles_by_subject(
                subject_id=user_id,
                subject_type=0,
                session=tm.session
            )

            return self._user_to_dict(user_obj, include_roles=True, roles=roles)

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

            self._check_system_role_assignment(user_in.role_ids, tm.session)

            try:
                new_user = user_repository.create_user(obj_in=user_in, session=tm.session)

                role_ids_to_assign = user_in.role_ids
                if not role_ids_to_assign or len(role_ids_to_assign) == 0:
                    from src.models.platform import Role
                    default_role = tm.session.execute(
                        Role.__table__.select().where(Role.code == RoleCodeConst.PLATFORM_NORMAL_USER.value)
                    ).first()
                    if default_role:
                        role_ids_to_assign = [default_role.id]
                        logger.info(f"用户 {user_in.username} 自动分配默认角色: {RoleCodeConst.PLATFORM_NORMAL_USER.value}")

                user_repository.update_roles(new_user, role_ids_to_assign, session=tm.session)

                tm.commit()

                # 获取用户角色
                roles = role_subject_repository.get_roles_by_subject(
                    subject_id=new_user.id,
                    subject_type=0,
                    session=tm.session
                )
                result = self._user_to_dict(new_user, include_roles=True, roles=roles)
                logger.info(f"用户创建成功: {user_in.username}")
                return result
            except IntegrityError as e:
                tm.rollback()
                logger.error(f"用户创建失败: {user_in.username}, 错误: {e}")
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail="用户创建失败，可能用户名或邮箱已存在",
                ) from e

    def update_user(self, user_id: int, user_in: UserUpdate) -> None:
        """更新用户（管理员）"""
        logger.info(f"更新用户: user_id={user_id}")

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户ID: {user_id} 不存在")

            if user_in.username and user_in.username != user.username:
                existing_user = user_repository.get_by_username(user_in.username, session=tm.session)
                if existing_user:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail=f"用户名 '{user_in.username}' 已存在",
                    )

            if user_in.email:
                # 检查邮箱是否已被绑定
                existing_bind = None
                for bind in user.account_binds:
                    if bind.bind_type == 1 and bind.identifier == user_in.email:
                        existing_bind = bind
                        break
                if not existing_bind:
                    existing_user = user_repository.get_by_email(user_in.email, session=tm.session)
                    if existing_user and existing_user.id != user.id:
                        raise BusinessException(
                            ResponseCode.PARAM_ERROR,
                            detail=f"邮箱 '{user_in.email}' 已存在",
                        )

            user_repository.update(id=user_id, obj_in=user_in, session=tm.session)

            self._check_system_role_assignment(user_in.role_ids, tm.session)

            if user_in.role_ids is not None:
                if len(user_in.role_ids) == 0:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail="用户必须至少绑定一个角色",
                    )

                user_repository.update_roles(user, user_in.role_ids, session=tm.session)

            tm.commit()

        clear_user_cache(user_id)
        logger.info(f"用户更新成功: user_id={user_id}")

    def delete_user(self, user_id: int) -> None:
        """删除用户（管理员）"""
        logger.info(f"删除用户: user_id={user_id}")

        with TransactionManager() as tm:
            success = user_repository.delete(id=user_id, session=tm.session)
            if not success:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户ID: {user_id} 不存在")

            tm.commit()

        clear_user_cache(user_id)
        logger.info(f"用户删除成功: user_id={user_id}")

    def reset_user_password(self, user_id: int) -> str:
        """重置用户密码（管理员）"""
        logger.info(f"重置用户密码: user_id={user_id}")

        with TransactionManager() as tm:
            result = user_repository.reset_password(user_id, session=tm.session)
            tm.commit()

        logger.info(f"用户密码重置成功: user_id={user_id}")
        return result

    def _build_user_search_filters(
        self,
        username: str = "",
        email: str = "",
        dept_id: int | None = None,
    ) -> list:
        """构建用户搜索过滤条件"""
        filters = []

        if username:
            filters.append(user_repository.model.username.contains(username))

        if email:
            # 因为 email 现在存储在 AccountBind 中，这里暂时不做搜索过滤
            pass

        if dept_id is not None:
            filters.append(user_repository.model.dept_id == dept_id)

        return filters

    def _transform_user_list_with_dept(self, items, session) -> list[dict]:
        """转换用户列表，添加部门信息和角色信息"""
        data = []

        for obj in items:
            # 通过 role_subject_repository 获取用户角色（subject_type=0 表示平台用户）
            roles = role_subject_repository.get_roles_by_subject(
                subject_id=obj.id,
                subject_type=0,
                session=session
            )
            user_dict = self._user_to_dict(obj, include_roles=True, roles=roles)

            dept_id = user_dict.pop("dept_id", None)
            if dept_id:
                dept_obj = dept_repository.get(id=dept_id, session=session)
                if dept_obj:
                    user_dict["dept"] = dept_obj.to_dict()
                else:
                    user_dict["dept"] = {}
            else:
                user_dict["dept"] = {}

            data.append(user_dict)

        return data


user_admin_service = UserAdminService()
