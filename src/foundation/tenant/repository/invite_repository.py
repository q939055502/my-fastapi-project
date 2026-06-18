import secrets
from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session
from src.models.tenant import Invite
from src.foundation.tenant.repository.base import TenantRepositoryBase


class InviteRepository(TenantRepositoryBase[Invite, None, None]):
    def __init__(self):
        super().__init__(model=Invite)

    def get_by_code(self, invite_code: str, session: Session) -> Invite | None:
        """根据邀请码获取邀请记录"""
        query = select(Invite).where(
            and_(
                Invite.invite_code == invite_code,
                Invite.status == True
            )
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().first()

    def get_pending_applications(self, tenant_id: int, session: Session) -> list[Invite]:
        """获取租户的待审核申请"""
        query = select(Invite).where(
            and_(
                Invite.tenant_id == tenant_id,
                Invite.invite_type == "apply",
                Invite.apply_status == 0
            )
        )
        query = self._apply_soft_delete_filter(query)
        return list(session.execute(query).scalars().all())

    def create_invite(
        self,
        tenant_id: int,
        invite_type: str,
        creator_member_id: int,
        default_role_id: int = None,
        need_audit: bool = False,
        target_contact: str = None,
        expire_hours: int = 72,
        session: Session = None
    ) -> Invite:
        """创建邀请记录"""
        invite_code = secrets.token_urlsafe(16) if invite_type in ("public", "private") else None
        expire_time = int((datetime.now().timestamp() + expire_hours * 3600) * 1000)

        invite = Invite(
            tenant_id=tenant_id,
            invite_type=invite_type,
            invite_code=invite_code,
            target_contact=target_contact,
            default_role_id=default_role_id,
            need_audit=need_audit,
            creator_member_id=creator_member_id,
            expire_time=expire_time,
            status=True
        )
        session.add(invite)
        return invite

    def create_application(
        self,
        tenant_id: int,
        apply_user_id: int,
        invite_code: str = None,
        session: Session = None
    ) -> Invite:
        """创建申请记录"""
        invite = Invite(
            tenant_id=tenant_id,
            invite_type="apply",
            invite_code=invite_code,
            apply_user_id=apply_user_id,
            apply_status=0,
            need_audit=True,
            status=True
        )
        session.add(invite)
        return invite

    def accept_application(self, invite_id: int, audit_member_id: int, session: Session) -> None:
        """通过申请"""
        session.execute(
            update(Invite).where(
                Invite.id == invite_id
            ).values(
                apply_status=1,
                audit_member_id=audit_member_id,
                audit_time=int(datetime.now().timestamp() * 1000)
            )
        )

    def reject_application(self, invite_id: int, audit_member_id: int, remark: str, session: Session) -> None:
        """拒绝申请"""
        session.execute(
            update(Invite).where(
                Invite.id == invite_id
            ).values(
                apply_status=2,
                audit_member_id=audit_member_id,
                audit_time=int(datetime.now().timestamp() * 1000),
                audit_remark=remark
            )
        )


tenant_invite_repository = InviteRepository()
