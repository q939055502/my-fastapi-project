from typing import List

from sqlalchemy import and_, delete, insert, select

from src.core.storage import BaseRepository
from src.models.platform import Role, RoleSubject


class RoleSubjectRepository(BaseRepository):
    model = RoleSubject

    def get_roles_by_subject(self, subject_id: int, subject_type: int, session=None) -> List[Role]:
        query = select(Role).join(
            self.model, self.model.role_id == Role.id
        ).where(
            and_(
                self.model.subject_id == subject_id,
                self.model.subject_type == subject_type
            )
        )
        # Role 需要软删除检查，RoleSubject 不需要
        query = query.where(Role.delete_time.is_(None))
        result = self._get_session(session).execute(query)
        return result.scalars().all()

    def get_role_ids_by_subject(self, subject_id: int, subject_type: int, session=None) -> List[int]:
        query = select(self.model.role_id).where(
            and_(
                self.model.subject_id == subject_id,
                self.model.subject_type == subject_type
            )
        )
        result = self._get_session(session).execute(query)
        return [row[0] for row in result]

    def get_subjects_by_role(self, role_id: int, subject_type: int = None, session=None) -> List[int]:
        query = select(self.model.subject_id).where(
            self.model.role_id == role_id
        )
        if subject_type is not None:
            query = query.where(self.model.subject_type == subject_type)
        result = self._get_session(session).execute(query)
        return [row[0] for row in result]

    def batch_create(self, role_id: int, subject_ids: List[int], subject_type: int, session=None) -> None:
        db = self._get_session(session)
        existing_ids = self.get_subjects_by_role(role_id, subject_type, session=db)
        new_ids = [sid for sid in subject_ids if sid not in existing_ids]

        if new_ids:
            records = [
                {"role_id": role_id, "subject_id": sid, "subject_type": subject_type}
                for sid in new_ids
            ]
            db.execute(insert(self.model), records)
            db.flush()

    def batch_remove(self, role_id: int, subject_ids: List[int], subject_type: int, session=None) -> None:
        db = self._get_session(session)
        db.execute(
            delete(self.model).where(
                and_(
                    self.model.role_id == role_id,
                    self.model.subject_id.in_(subject_ids),
                    self.model.subject_type == subject_type
                )
            )
        )
        db.flush()

    def remove_by_subject(self, subject_id: int, subject_type: int, session=None) -> None:
        db = self._get_session(session)
        db.execute(
            delete(self.model).where(
                and_(
                    self.model.subject_id == subject_id,
                    self.model.subject_type == subject_type
                )
            )
        )
        db.flush()


role_subject_repository = RoleSubjectRepository(model=RoleSubject)
