"""
账号绑定仓库 - 处理手机号/邮箱绑定的数据访问
"""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from src.common.core.constants import AccountBindStatusConst
from src.common.repository.base import GenericRepository
from src.models.platform.account_bind import AccountBind


class AccountBindRepository(GenericRepository[AccountBind, None, None]):

    def __init__(self):
        super().__init__(model=AccountBind)

    def get_user_bindings(self, user_id: int, session: Session) -> list[AccountBind]:
        """获取用户的所有绑定"""
        query = select(AccountBind).where(AccountBind.user_id == user_id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return list(result.scalars().all())

    def get_by_identifier(
        self, bind_type: int, identifier: str, session: Session, status: str | None = None
    ) -> AccountBind | None:
        """根据绑定类型和标识查找绑定"""
        query = select(AccountBind).where(
            and_(
                AccountBind.bind_type == bind_type,
                AccountBind.identifier == identifier
            )
        )
        if status:
            query = query.where(AccountBind.status == status)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_user_and_type(
        self, user_id: int, bind_type: int, session: Session
    ) -> AccountBind | None:
        """获取用户指定类型的绑定（优先默认）"""
        query = select(AccountBind).where(
            and_(
                AccountBind.user_id == user_id,
                AccountBind.bind_type == bind_type
            )
        ).order_by(AccountBind.is_default.desc())
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def create_bind(
        self,
        user_id: int,
        bind_type: int,
        identifier: str,
        is_default: bool = False,
        status: str = None,
        source: str = "manual",
        session: Session = None,
    ) -> AccountBind:
        """创建新的绑定"""
        if status is None:
            status = AccountBindStatusConst.PENDING.value
        bind_data = {
            "user_id": user_id,
            "bind_type": bind_type,
            "identifier": identifier,
            "is_default": 1 if is_default else 0,
            "status": status,
            "source": source,
        }
        return self.create(bind_data, session=session)

    def set_default(self, user_id: int, bind_id: int, session: Session) -> AccountBind | None:
        """设置默认绑定"""
        bind = self.get(id=bind_id, session=session)
        if not bind or bind.user_id != user_id:
            return None

        update_query = (
            self.model.__table__.update()
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.bind_type == bind.bind_type
                )
            )
            .values(is_default=False)
        )
        session.execute(update_query)

        bind.is_default = True
        return bind

    def verify_bind(self, bind_id: int, user_id: int, session: Session) -> AccountBind | None:
        """验证绑定"""
        from datetime import datetime
        bind = self.get(id=bind_id, session=session)
        if not bind or bind.user_id != user_id:
            return None

        bind.status = "verified"
        bind.verified_at = datetime.now()
        return bind

    def disable_bind(self, bind_id: int, user_id: int, session: Session) -> AccountBind | None:
        """禁用绑定"""
        bind = self.get(id=bind_id, session=session)
        if not bind or bind.user_id != user_id:
            return None

        bind.status = "disabled"
        return bind

    def delete_bind(self, bind_id: int, user_id: int, session: Session) -> bool:
        """删除绑定（软删除）"""
        bind = self.get(id=bind_id, session=session)
        if not bind or bind.user_id != user_id:
            return False

        self.soft_delete(id=bind_id, session=session)
        return True

    def get_phone(self, user_id: int, session: Session) -> str | None:
        """获取用户绑定的手机号"""
        query = select(AccountBind).where(
            and_(
                AccountBind.user_id == user_id,
                AccountBind.bind_type == 0,  # 0=手机号
                AccountBind.status == "verified"
            )
        ).order_by(AccountBind.is_default.desc())
        result = session.execute(query)
        bind = result.scalars().first()
        return bind.identifier if bind else None

    def get_email(self, user_id: int, session: Session) -> str | None:
        """获取用户绑定的邮箱"""
        query = select(AccountBind).where(
            and_(
                AccountBind.user_id == user_id,
                AccountBind.bind_type == 1,  # 1=邮箱
                AccountBind.status == "verified"
            )
        ).order_by(AccountBind.is_default.desc())
        result = session.execute(query)
        bind = result.scalars().first()
        return bind.identifier if bind else None


account_bind_repository = AccountBindRepository()
