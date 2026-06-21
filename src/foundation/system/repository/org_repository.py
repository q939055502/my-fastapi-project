from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from src.core.log import logger
from src.core.storage import BaseRepository
from src.foundation.system.schemas.org import OrgCreate, OrgUpdate
from src.models.platform import Org, OrgClosure


class OrgRepository(BaseRepository[Org, OrgCreate, OrgUpdate]):
    def __init__(self):
        super().__init__(model=Org)

    def get_org_tree(self, name: str, session: Session):
        query = select(Org)
        query = self._apply_soft_delete_filter(query)

        if name:
            query = query.where(Org.name.contains(name))

        result = session.execute(query.order_by(Org.sort))
        all_orgs = result.scalars().all()

        # 构建 parent_uuid 映射(通过 OrgClosure 查询父节点)
        parent_map = {}
        for org in all_orgs:
            if org.parent_id:
                parent_org = next((o for o in all_orgs if o.id == org.parent_id), None)
                parent_map[org.uuid] = parent_org.uuid if parent_org else None
            else:
                parent_map[org.uuid] = None

        def build_tree(parent_uuid):
            return [
                {
                    "uuid": org.uuid,
                    "name": org.name,
                    "remark": org.remark,
                    "sort": org.sort,
                    "parent_uuid": parent_map.get(org.uuid),
                    "children": build_tree(org.uuid),
                }
                for org in all_orgs
                if parent_map.get(org.uuid) == parent_uuid
            ]

        org_tree = build_tree(None)
        return org_tree

    def get_org_info(self, session: Session):
        pass

    def update_org_closure(self, obj: Org, session: Session):
        parent_id = obj.parent_id

        result = session.execute(
            select(OrgClosure).where(OrgClosure.descendant == parent_id)
        )
        parent_orgs = result.scalars().all()

        for i in parent_orgs:
            logger.debug(
                f"Processing org closure: ancestor={i.ancestor}, descendant={i.descendant}"
            )

        org_closure_objs: list[OrgClosure] = []
        for item in parent_orgs:
            org_closure_objs.append(
                OrgClosure(
                    ancestor=item.ancestor,
                    descendant=obj.id,
                    level=item.level + 1,
                )
            )
        org_closure_objs.append(
            OrgClosure(ancestor=obj.id, descendant=obj.id, level=0)
        )
        session.add_all(org_closure_objs)

    def create_org(self, obj_in: OrgCreate, session: Session):
        if obj_in.parent_uuid:
            from src.core.storage.uuid_resolver import uuid_resolver

            parent_id = uuid_resolver.resolve(session, "org", obj_in.parent_uuid)
            if parent_id:
                obj_in.parent_id = parent_id
        new_obj = self.create(obj_in=obj_in, session=session)
        self.update_org_closure(new_obj, session=session)

    def update_org(self, org_id: int, obj_in: OrgUpdate, session: Session):
        org_obj = self.get(id=org_id, session=session)
        if not org_obj:
            return

        old_parent_id = org_obj.parent_id
        new_parent_id = None

        if obj_in.parent_uuid:
            from src.core.storage.uuid_resolver import uuid_resolver

            parent_id = uuid_resolver.resolve(session, "org", obj_in.parent_uuid)
            new_parent_id = parent_id if parent_id else None

        if old_parent_id != new_parent_id:
            session.execute(
                delete(OrgClosure).where(
                    and_(
                        (OrgClosure.ancestor == org_obj.id) |
                        (OrgClosure.descendant == org_obj.id)
                    )
                )
            )
            org_obj.parent_id = new_parent_id
            self.update_org_closure(org_obj, session=session)

        self.update(id=org_obj.id, obj_in=obj_in, session=session)

    def delete_org(self, org_id: int, session: Session):
        org_obj = self.get(id=org_id, session=session)
        if org_obj:
            self.delete(org_obj.id, session=session)
            session.execute(
                delete(OrgClosure).where(OrgClosure.descendant == org_obj.id)
            )


org_repository = OrgRepository()
