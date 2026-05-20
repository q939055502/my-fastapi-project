from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from src.models.sys import Resource
from src.schemas.sys.resource import ResourceCreate, ResourceUpdate
from src.core.storage.generic_repository import GenericRepository


class ResourceRepository(GenericRepository[Resource, ResourceCreate, ResourceUpdate]):
    def __init__(self):
        super().__init__(model=Resource)

    def get_by_code(self, code: str, session: Session) -> Resource | None:
        query = select(Resource).where(Resource.code == code)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalar_one_or_none()

    def get_by_code_with_deleted(self, code: str, session: Session) -> Resource | None:
        return session.execute(
            select(Resource).where(Resource.code == code)
        ).scalar_one_or_none()

    def get_by_api_path(self, api_path: str, api_method: str, session: Session) -> Resource | None:
        query = select(Resource).where(
            and_(
                Resource.api_path == api_path,
                Resource.api_method == api_method,
                Resource.status == 1
            )
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalar_one_or_none()

    def get_by_api_path_with_deleted(self, api_path: str, api_method: str, session: Session) -> Resource | None:
        return session.execute(
            select(Resource).where(
                and_(
                    Resource.api_path == api_path,
                    Resource.api_method == api_method,
                    Resource.status == 1
                )
            )
        ).scalar_one_or_none()

    def get_children(self, parent_id: int, session: Session) -> list[Resource]:
        query = select(Resource).where(
            and_(
                Resource.parent_id == parent_id,
                Resource.status == 1
            )
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(
            query.order_by(Resource.sort.asc())
        ).scalars().all()

    def get_children_with_deleted(self, parent_id: int, session: Session) -> list[Resource]:
        return session.execute(
            select(Resource).where(
                and_(
                    Resource.parent_id == parent_id,
                    Resource.status == 1
                )
            ).order_by(Resource.sort.asc())
        ).scalars().all()

    def exists_by_code(self, code: str, exclude_id: int | None = None, session: Session = None) -> bool:
        query = select(Resource).where(Resource.code == code)
        query = self._apply_soft_delete_filter(query)
        if exclude_id:
            query = query.where(Resource.id != exclude_id)
        return session.execute(query).first() is not None

    def exists_by_code_with_deleted(self, code: str, exclude_id: int | None = None, session: Session = None) -> bool:
        query = select(Resource).where(Resource.code == code)
        if exclude_id:
            query = query.where(Resource.id != exclude_id)
        return session.execute(query).first() is not None

    def get_resources_by_role(self, role_id: int, session: Session) -> list[Resource]:
        from src.models.sys.associations import role_resource_association
        query = select(Resource).join(role_resource_association).where(
            and_(
                role_resource_association.c.role_id == role_id,
                Resource.status == 1
            )
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def get_by_id(self, id: int, session: Session) -> Resource | None:
        query = select(Resource).where(Resource.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()


resource_repository = ResourceRepository()
