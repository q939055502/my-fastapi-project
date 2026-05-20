from fastapi.exceptions import HTTPException
from sqlalchemy import and_, or_, desc
from sqlalchemy.exc import IntegrityError

from src.repositories.sys.dept_repository import dept_repository
from src.repositories.sys.user_repository import user_repository
from src.repositories.sys.role_repository import role_repository
from src.schemas.sys.users import UserCreate, UserUpdate
from src.core.log import logger
from src.core.storage import UnitOfWork
from src.core.storage import cached, clear_user_cache
from src.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self):
        self.logger = logger

    def _check_system_role_assignment(self, role_ids: list[int], session) -> None:
        if not role_ids:
            return

        roles = session.execute(
            role_repository.model.__table__.select()
            .where(role_repository.model.id.in_(role_ids))
        ).scalars().all()

        for role in roles:
            if role.is_system:
                raise HTTPException(
                    status_code=403,
                    detail=f"禁止分配系统内置角色 '{role.name}'",
                )

    def get_user_list(
        self,
        page: int = 1,
        page_size: int = 10,
        username: str = "",
        email: str = "",
        dept_id: int | None = None,
    ) -> tuple[int, list[dict]]:
        with UnitOfWork() as uow:
            search_filters = self._build_user_search_filters(
                username=username, email=email, dept_id=dept_id
            )

            total, items = user_repository.list(
                page=page,
                page_size=page_size,
                session=uow.session,
                filters=search_filters,
                order_by=[desc(user_repository.model.created_at)],
                eager_load=[user_repository.model.roles],
            )

            data = self._transform_user_list_with_dept(items, uow.session)

            return total, data

    @cached("user_detail", ttl=300)
    def get_user_detail(self, user_id: int) -> dict:
        with UnitOfWork() as uow:
            user_obj = user_repository.get_with_roles(id=user_id, session=uow.session)
            if not user_obj:
                raise HTTPException(status_code=404, detail=f"用户ID: {user_id} 不存在")

            user_dict = {}
            for column in user_obj.__table__.columns:
                field_name = column.name
                if field_name != "password":
                    value = getattr(user_obj, field_name)
                    user_dict[field_name] = value
            
            user_dict["roles"] = []
            for role in user_obj.roles:
                role_dict = {
                    "id": role.id,
                    "name": role.name,
                    "remark": role.remark
                }
                user_dict["roles"].append(role_dict)

            return user_dict

    def create_user(self, user_in: UserCreate) -> dict:
        with UnitOfWork() as uow:
            existing_user_by_username = user_repository.get_by_username(user_in.username, session=uow.session)
            if existing_user_by_username:
                raise HTTPException(
                    status_code=400,
                    detail=f"用户名 '{user_in.username}' 已存在",
                )

            existing_user_by_email = user_repository.get_by_email(user_in.email, session=uow.session)
            if existing_user_by_email:
                raise HTTPException(
                    status_code=400,
                    detail=f"邮箱 '{user_in.email}' 已存在",
                )

            self._check_system_role_assignment(user_in.role_ids, uow.session)

            try:
                new_user = user_repository.create_user(obj_in=user_in, session=uow.session)

                role_ids_to_assign = user_in.role_ids
                if not role_ids_to_assign or len(role_ids_to_assign) == 0:
                    from src.models.sys.role import Role
                    default_role = uow.session.execute(
                        Role.__table__.select().where(Role.name == "平台普通用户")
                    ).first()
                    if default_role:
                        role_ids_to_assign = [default_role.id]

                user_repository.update_roles(new_user, role_ids_to_assign, session=uow.session)

                uow.commit()

                user_dict = {}
                for column in new_user.__table__.columns:
                    field_name = column.name
                    if field_name != "password":
                        value = getattr(new_user, field_name)
                        user_dict[field_name] = value
                
                user_dict["roles"] = []
                for role in new_user.roles:
                    role_dict = {
                        "id": role.id,
                        "name": role.name
                    }
                    user_dict["roles"].append(role_dict)
                
                return user_dict
            except IntegrityError as e:
                uow.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="用户创建失败，可能用户名或邮箱已存在",
                ) from e

    def update_user(self, user_id: int, user_in: UserUpdate) -> None:
        with UnitOfWork() as uow:
            user = user_repository.get(id=user_id, session=uow.session)
            if not user:
                raise HTTPException(status_code=404, detail=f"用户ID: {user_id} 不存在")

            if user_in.username and user_in.username != user.username:
                existing_user = user_repository.get_by_username(user_in.username, session=uow.session)
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail=f"用户名 '{user_in.username}' 已存在",
                    )

            if user_in.email and user_in.email != user.email:
                existing_user = user_repository.get_by_email(user_in.email, session=uow.session)
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail=f"邮箱 '{user_in.email}' 已存在",
                    )

            user_repository.update(id=user_id, obj_in=user_in, session=uow.session)

            self._check_system_role_assignment(user_in.role_ids, uow.session)

            if user_in.role_ids is not None:
                if len(user_in.role_ids) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="用户必须至少绑定一个角色",
                    )
                
                user_repository.update_roles(user, user_in.role_ids, session=uow.session)

            uow.commit()

        clear_user_cache(user_id)

    def delete_user(self, user_id: int) -> None:
        with UnitOfWork() as uow:
            success = user_repository.delete(id=user_id, session=uow.session)
            if not success:
                raise HTTPException(status_code=404, detail=f"用户ID: {user_id} 不存在")

            uow.commit()

        clear_user_cache(user_id)

    def reset_user_password(self, user_id: int) -> str:
        with UnitOfWork() as uow:
            result = user_repository.reset_password(user_id, session=uow.session)
            uow.commit()
            return result

    def change_user_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        with UnitOfWork() as uow:
            user = user_repository.get(id=user_id, session=uow.session)
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            if not verify_password(old_password, user.password):
                return False
            
            user.password = get_password_hash(new_password)
            uow.commit()
        
        clear_user_cache(user_id)
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
            user_dict = {}
            for column in obj.__table__.columns:
                field_name = column.name
                if field_name != "password":
                    value = getattr(obj, field_name)
                    user_dict[field_name] = value
            
            user_dict["roles"] = []
            for role in obj.roles:
                role_dict = {
                    "id": role.id,
                    "name": role.name
                }
                user_dict["roles"].append(role_dict)

            dept_id = user_dict.pop("dept_id", None)
            if dept_id:
                dept_obj = dept_repository.get(id=dept_id, session=session)
                if dept_obj:
                    dept_dict = {}
                    for column in dept_obj.__table__.columns:
                        dept_dict[column.name] = getattr(dept_obj, column.name)
                    user_dict["dept"] = dept_dict
                else:
                    user_dict["dept"] = {}
            else:
                user_dict["dept"] = {}

            data.append(user_dict)

        return data


user_service = UserService()
