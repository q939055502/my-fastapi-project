import secrets
from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session
from src.common.repository.base import GenericRepository
from src.models.tenant import TenantInvite


class TenantInviteRepository(GenericRepository[TenantInvite, None, None]):
    def __init__(self):
        super().__init__(model=TenantInvite)

    def get_by_code(self, invite_code: str, session: Session) -> TenantInvite | None:
        """根据邀请码获取邀请记录"""
        query = select(TenantInvite).where(
            and_(
                TenantInvite.invite_code == invite_code,
                TenantInvite.status == 1,
                not TenantInvite.is_deleted
            )
        )
        return session.execute(query).scalars().first()

    def get_pending_applications(self, tenant_id: int, session: Session) -> list[TenantInvite]:
        """获取租户的待审核申请"""
        query = select(TenantInvite).where(
            and_(
                TenantInvite.tenant_id == tenant_id,
                TenantInvite.invite_type == "apply",
                TenantInvite.apply_status == 0,
                not TenantInvite.is_deleted
            )
        )
        return list(session.execute(query).scalars().all())

    def create_invite(
        self,
        tenant_id: int,
        invite_type: str,
        creator_member_id: int,
        default_role_id: int = None,
        need_audit: int = 0,
        target_contact: str = None,
        expire_hours: int = 72,
        session: Session = None
    ) -> TenantInvite:
        """创建邀请记录"""
        invite_code = secrets.token_urlsafe(16) if invite_type in ("public", "private") else None
        expire_time = int((datetime.now().timestamp() + expire_hours * 3600) * 1000)

        invite = TenantInvite(
            tenant_id=tenant_id,
            invite_type=invite_type,
            invite_code=invite_code,
            target_contact=target_contact,
            default_role_id=default_role_id,
            need_audit=need_audit,
            creator_member_id=creator_member_id,
            expire_time=expire_time,
            status=1
        )
        session.add(invite)
        return invite

    def create_application(
        self,
        tenant_id: int,
        apply_user_id: int,
        invite_code: str = None,
        session: Session = None
    ) -> TenantInvite:
        """创建申请记录"""
        invite = TenantInvite(
            tenant_id=tenant_id,
            invite_type="apply",
            invite_code=invite_code,
            apply_user_id=apply_user_id,
            apply_status=0,
            need_audit=1,
            status=1
        )
        session.add(invite)
        return invite

    def accept_application(self, invite_id: int, audit_member_id: int, session: Session) -> None:
        """通过申请"""
        session.execute(
            update(TenantInvite).where(
                TenantInvite.id == invite_id
            ).values(
                apply_status=1,
                audit_member_id=audit_member_id,
                audit_time=int(datetime.now().timestamp() * 1000)
            )
        )

    def reject_application(self, invite_id: int, audit_member_id: int, remark: str, session: Session) -> None:
        """拒绝申请"""
        session.execute(
            update(TenantInvite).where(
                TenantInvite.id == invite_id
            ).values(
                apply_status=2,
                audit_member_id=audit_member_id,
                audit_time=int(datetime.now().timestamp() * 1000),
                audit_remark=remark
            )
        )


tenant_invite_repository = TenantInviteRepository()
