from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from src.common.core.log import logger
from src.common.repository.base import GenericRepository
from src.models.platform import Dept, DeptClosure
from src.foundation.platform.schemas.dept import DeptCreate, DeptUpdate


class DeptRepository(GenericRepository[Dept, DeptCreate, DeptUpdate]):
    def __init__(self):
        super().__init__(model=Dept)

    def get_dept_tree(self, name: str, session: Session):
        query = select(Dept).where(Dept.delete_time.is_(None))

        if name:
            query = query.where(Dept.name.contains(name))

        result = session.execute(query.order_by(Dept.sort))
        all_depts = result.scalars().all()

        def build_tree(parent_uuid):
            return [
                {
                    "uuid": dept.uuid,
                    "name": dept.name,
                    "remark": dept.remark,
                    "sort": dept.sort,
                    "parent_uuid": dept.parent_uuid,
                    "children": build_tree(dept.uuid),
                }
                for dept in all_depts
                if dept.parent_uuid == parent_uuid
            ]

        dept_tree = build_tree(None)
        return dept_tree

    def get_dept_info(self, session: Session):
        pass

    def update_dept_closure(self, obj: Dept, session: Session):
        parent_id = obj.parent_id
        if obj.parent_uuid:
            parent_dept = self.get_by_uuid(obj.parent_uuid, session)
            parent_id = parent_dept.id if parent_dept else None
        
        result = session.execute(
            select(DeptClosure).where(DeptClosure.descendant == parent_id)
        )
        parent_depts = result.scalars().all()

        for i in parent_depts:
            logger.debug(
                f"Processing dept closure: ancestor={i.ancestor}, descendant={i.descendant}"
            )

        dept_closure_objs: list[DeptClosure] = []
        for item in parent_depts:
            dept_closure_objs.append(
                DeptClosure(
                    ancestor=item.ancestor,
                    descendant=obj.id,
                    level=item.level + 1,
                )
            )
        dept_closure_objs.append(
            DeptClosure(ancestor=obj.id, descendant=obj.id, level=0)
        )
        session.add_all(dept_closure_objs)

    def create_dept(self, obj_in: DeptCreate, session: Session):
        if obj_in.parent_uuid:
            parent_dept = self.get_by_uuid(uuid=obj_in.parent_uuid, session=session)
            if parent_dept:
                obj_in.parent_id = parent_dept.id
        new_obj = self.create(obj_in=obj_in, session=session)
        self.update_dept_closure(new_obj, session=session)

    def update_dept(self, dept_uuid: UUID, obj_in: DeptUpdate, session: Session):
        dept_obj = self.get_by_uuid(uuid=dept_uuid, session=session)
        if not dept_obj:
            return

        old_parent_id = dept_obj.parent_id
        new_parent_id = None
        
        if obj_in.parent_uuid:
            parent_dept = self.get_by_uuid(uuid=obj_in.parent_uuid, session=session)
            new_parent_id = parent_dept.id if parent_dept else None

        if old_parent_id != new_parent_id:
            session.execute(
                delete(DeptClosure).where(
                    and_(
                        (DeptClosure.ancestor == dept_obj.id) |
                        (DeptClosure.descendant == dept_obj.id)
                    )
                )
            )
            dept_obj.parent_id = new_parent_id
            self.update_dept_closure(dept_obj, session=session)
        
        self.update(id=dept_obj.id, obj_in=obj_in, session=session)

    def delete_dept(self, dept_uuid: UUID, session: Session):
        dept_obj = self.get_by_uuid(uuid=dept_uuid, session=session)
        if dept_obj:
            self.delete(dept_obj.id, session=session)
            session.execute(
                delete(DeptClosure).where(DeptClosure.descendant == dept_obj.id)
            )


dept_repository = DeptRepository()