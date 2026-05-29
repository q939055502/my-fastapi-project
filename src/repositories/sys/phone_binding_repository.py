from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.storage.generic_repository import GenericRepository
from src.models.iam import PhoneBinding


class PhoneBindingRepository(GenericRepository[PhoneBinding, dict, dict]):

    def __init__(self):
        super().__init__(model=PhoneBinding)

    def get_by_phone(self, phone: str, session: Session) -> PhoneBinding | None:
        query = select(PhoneBinding).where(PhoneBinding.phone == phone)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_user_id(self, user_id: int, session: Session) -> list[PhoneBinding]:
        query = select(PhoneBinding).where(PhoneBinding.user_id == user_id)
        result = session.execute(query)
        return result.scalars().all()

    def get_primary_binding(self, phone: str, session: Session) -> PhoneBinding | None:
        query = select(PhoneBinding).where(
            PhoneBinding.phone == phone,
            PhoneBinding.is_primary
        )
        result = session.execute(query)
        return result.scalars().first()

    def get_secondary_bindings(self, phone: str, session: Session) -> list[PhoneBinding]:
        query = select(PhoneBinding).where(
            PhoneBinding.phone == phone,
            not PhoneBinding.is_primary
        )
        result = session.execute(query)
        return result.scalars().all()

    def is_phone_bound(self, phone: str, session: Session) -> bool:
        query = select(PhoneBinding).where(PhoneBinding.phone == phone)
        result = session.execute(query)
        return result.scalars().first() is not None

    def create_binding(self, phone: str, user_id: int, is_primary: bool, session: Session) -> PhoneBinding:
        obj_dict = {
            "phone": phone,
            "user_id": user_id,
            "is_primary": is_primary
        }
        db_obj = PhoneBinding(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)
        return db_obj

    def delete_by_user_id(self, user_id: int, session: Session) -> None:
        bindings = self.get_by_user_id(user_id, session)
        for binding in bindings:
            session.delete(binding)


phone_binding_repository = PhoneBindingRepository()
