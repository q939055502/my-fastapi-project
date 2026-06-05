from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from src.core.auth import get_password_hash, verify_password
from src.core.constants import ROLE_PLATFORM_NORMAL_USER
from src.core.enums.response_code import ResponseCode
from src.core.exceptions.exception import BusinessException
from src.core.log import logger
from src.core.storage.cache.cache_manager import cache_manager, clear_user_cache
from src.core.storage.transaction_manager import TransactionManager
from src.repositories.iam.dept_repository import dept_repository
from src.repositories.iam.role_repository import role_repository
from src.repositories.iam.user_repository import user_repository
from src.schemas.iam.user import UserCreate, UserUpdate


class UserService:
    def _check_system_role_assignment(self, role_ids: list[int], session) -> None:
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

    def _user_to_dict(self, user_obj, include_roles: bool = True) -> dict:
        """将用户对象转换为字典，排除密码字段"""
        user_dict = user_obj.to_dict(exclude_fields=["password"])

        if include_roles and hasattr(user_obj, "roles"):
            user_dict["roles"] = [
                {
                    "id": role.id,
                    "name": role.name,
                    "remark": role.remark
                }
                for role in user_obj.roles
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
                eager_load=[user_repository.model.roles],
            )

            data = self._transform_user_list_with_dept(items, tm.session)

            return total, data

    @cache_manager.cached("user_detail", ttl=300)
    def get_user_detail(self, user_id: int) -> dict:
        with TransactionManager() as tm:
            user_obj = user_repository.get_with_roles(id=user_id, session=tm.session)
            if not user_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户ID: {user_id} 不存在")

            return self._user_to_dict(user_obj, include_roles=True)

    def create_user(self, user_in: UserCreate) -> dict:
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
                    from src.models.iam import Role
                    default_role = tm.session.execute(
                        Role.__table__.select().where(Role.name == ROLE_PLATFORM_NORMAL_USER)
                    ).first()
                    if default_role:
                        role_ids_to_assign = [default_role.id]
                        logger.info(f"用户 {user_in.username} 自动分配默认角色: {ROLE_PLATFORM_NORMAL_USER}")

                user_repository.update_roles(new_user, role_ids_to_assign, session=tm.session)

                tm.commit()

                result = self._user_to_dict(new_user, include_roles=True)
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

            if user_in.email and user_in.email != user.email:
                existing_user = user_repository.get_by_email(user_in.email, session=tm.session)
                if existing_user:
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
        logger.info(f"删除用户: user_id={user_id}")

        with TransactionManager() as tm:
            success = user_repository.delete(id=user_id, session=tm.session)
            if not success:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail=f"用户ID: {user_id} 不存在")

            tm.commit()

        clear_user_cache(user_id)
        logger.info(f"用户删除成功: user_id={user_id}")

    def reset_user_password(self, user_id: int) -> str:
        logger.info(f"重置用户密码: user_id={user_id}")

        with TransactionManager() as tm:
            result = user_repository.reset_password(user_id, session=tm.session)
            tm.commit()

        logger.info(f"用户密码重置成功: user_id={user_id}")
        return result

    def change_user_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        logger.info(f"修改用户密码: user_id={user_id}")

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="用户不存在")

            if not verify_password(old_password, user.password):
                logger.warning(f"用户密码修改失败: 旧密码错误, user_id={user_id}")
                return False

            user.password = get_password_hash(new_password)
            tm.commit()

        clear_user_cache(user_id)
        logger.info(f"用户密码修改成功: user_id={user_id}")
        return True

    def _build_user_search_filters(
        self,
        username: str = "",
        email: str = "",
        dept_id: int | None = None,
    ) -> list:
        filters = []

        if username:
            filters.append(user_repository.model.username.contains(username))

        if email:
            filters.append(user_repository.model.email.contains(email))

        if dept_id is not None:
            filters.append(user_repository.model.dept_id == dept_id)

        return filters

    def _transform_user_list_with_dept(self, items, session) -> list[dict]:
        data = []

        for obj in items:
            user_dict = self._user_to_dict(obj, include_roles=True)

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


user_service = UserService()
