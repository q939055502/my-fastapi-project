
from sqlalchemy import and_, delete, insert, select

from src.core.storage import BaseRepository
from src.models.platform import RoleSubject


class RoleSubjectRepository(BaseRepository):
    """角色-主体关联 Repository

    仅负责关联关系的增删操作,不负责查询。
    查询由调用方组合 RoleRepository 和 RoleSubjectRepository 完成。
    """
    model = RoleSubject

    def get_role_ids_by_subject(self, subject_id: int, subject_type: int, session=None) -> list[int]:
        """获取主体关联的角色ID列表"""
        query = select(self.model.role_id).where(
            and_(
                self.model.subject_id == subject_id,
                self.model.subject_type == subject_type
            )
        )
        result = self._get_session(session).execute(query)
        return [row[0] for row in result]

    def batch_create(self, role_id: int, subject_ids: list[int], subject_type: int, session=None) -> None:
        """批量创建角色-主体关联"""
        db = self._get_session(session)
        existing_ids = self.get_role_ids_by_subject(subject_ids[0] if subject_ids else 0, subject_type, session=db)
        new_ids = [sid for sid in subject_ids if sid not in existing_ids]

        if new_ids:
            records = [
                {"role_id": role_id, "subject_id": sid, "subject_type": subject_type}
                for sid in new_ids
            ]
            db.execute(insert(self.model), records)
            db.flush()

    def batch_remove(self, role_id: int, subject_ids: list[int], subject_type: int, session=None) -> None:
        """批量移除角色-主体关联"""
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
        """根据主体移除所有关联"""
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
