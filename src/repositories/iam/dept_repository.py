from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from src.core.log import logger
from src.models.iam import Dept, DeptClosure
from src.repositories.base import GenericRepository
from src.schemas.iam.dept import DeptCreate, DeptUpdate


class DeptRepository(GenericRepository[Dept, DeptCreate, DeptUpdate]):
    def __init__(self):
        super().__init__(model=Dept)

    def get_dept_tree(self, name: str, session: Session):
        query = select(Dept).where(not Dept.is_deleted)

        if name:
            query = query.where(Dept.name.contains(name))

        result = session.execute(query.order_by(Dept.sort))
        all_depts = result.scalars().all()

        def build_tree(parent_id):
            return [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "remark": dept.remark,
                    "sort": dept.sort,
                    "parent_id": dept.parent_id,
                    "children": build_tree(dept.id),
                }
                for dept in all_depts
                if dept.parent_id == parent_id
            ]

        dept_tree = build_tree(None)
        return dept_tree

    def get_dept_info(self, session: Session):
        pass

    def update_dept_closure(self, obj: Dept, session: Session):
        result = session.execute(
            select(DeptClosure).where(DeptClosure.descendant == obj.parent_id)
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
        if obj_in.parent_id != 0:
            self.get(id=obj_in.parent_id, session=session)
        new_obj = self.create(obj_in=obj_in, session=session)
        self.update_dept_closure(new_obj, session=session)

    def update_dept(self, dept_id: int, obj_in: DeptUpdate, session: Session):
        dept_obj = self.get(id=dept_id, session=session)
        if dept_obj.parent_id != obj_in.parent_id:
            session.execute(
                delete(DeptClosure).where(
                    and_(
                        (DeptClosure.ancestor == dept_obj.id) |
                        (DeptClosure.descendant == dept_obj.id)
                    )
                )
            )
            dept_obj.parent_id = obj_in.parent_id
            self.update_dept_closure(dept_obj, session=session)
        self.update(id=dept_id, obj_in=obj_in, session=session)

    def delete_dept(self, dept_id: int, session: Session):
        dept_obj = self.get(id=dept_id, session=session)
        if dept_obj:
            self.delete(dept_id, session=session)
            session.execute(
                delete(DeptClosure).where(DeptClosure.descendant == dept_id)
            )


dept_repository = DeptRepository()
