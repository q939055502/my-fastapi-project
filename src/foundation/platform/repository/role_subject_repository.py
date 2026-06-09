from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload
from src.common.repository.base import GenericRepository
from src.models.platform import RoleSubject
from src.foundation.platform.schemas.role_subject import (
    RoleSubjectCreate,
    RoleSubjectUpdate,
)


class RoleSubjectRepository(GenericRepository[RoleSubject, RoleSubjectCreate, RoleSubjectUpdate]):
    def __init__(self):
        super().__init__(model=RoleSubject)

    def get_by_subject(self, subject_id: int, subject_type: int, session: Session) -> list[RoleSubject]:
        """根据主体获取所有角色关联"""
        query = select(RoleSubject).where(
            RoleSubject.subject_id == subject_id,
            RoleSubject.subject_type == subject_type
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def get_by_role_id(self, role_id: int, session: Session) -> list[RoleSubject]:
        """根据角色ID获取所有主体关联"""
        query = select(RoleSubject).where(RoleSubject.role_id == role_id)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def delete_by_subject(self, subject_id: int, subject_type: int, session: Session) -> None:
        """删除主体的所有角色关联"""
        session.execute(delete(RoleSubject).where(
            RoleSubject.subject_id == subject_id,
            RoleSubject.subject_type == subject_type
        ))

    def delete_by_role_id(self, role_id: int, session: Session) -> None:
        """删除角色的所有主体关联"""
        session.execute(delete(RoleSubject).where(RoleSubject.role_id == role_id))

    def batch_create(self, role_id: int, subjects: list[tuple[int, int]], created_by: int | None = None, session: Session = None) -> None:
        """批量创建角色主体关联

        Args:
            subjects: [(subject_id, subject_type), ...]
        """
        for subject_id, subject_type in subjects:
            role_subj = RoleSubject(
                subject_id=subject_id,
                subject_type=subject_type,
                role_id=role_id,
                created_by=created_by
            )
            session.add(role_subj)

    def is_exist(self, subject_id: int, subject_type: int, role_id: int, session: Session) -> bool:
        """检查角色主体关联是否已存在"""
        query = select(RoleSubject).where(
            RoleSubject.subject_id == subject_id,
            RoleSubject.subject_type == subject_type,
            RoleSubject.role_id == role_id
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None

    def get_roles_by_subject(self, subject_id: int, subject_type: int, session: Session) -> list:
        """根据主体获取关联的角色列表

        Args:
            subject_id: 主体ID（用户ID或成员ID）
            subject_type: 主体类型（0=平台用户，1=租户成员）
            session: 数据库会话

        Returns:
            Role 对象列表
        """
        query = (
            select(RoleSubject)
            .where(
                RoleSubject.subject_id == subject_id,
                RoleSubject.subject_type == subject_type
            )
            .options(selectinload(RoleSubject.role))
        )
        query = self._apply_soft_delete_filter(query)
        role_subjects = session.execute(query).scalars().all()

        # 提取角色对象
        roles = []
        seen_ids = set()
        for rs in role_subjects:
            if rs.role and rs.role.id not in seen_ids:
                roles.append(rs.role)
                seen_ids.add(rs.role.id)
        return roles


role_subject_repository = RoleSubjectRepository()
