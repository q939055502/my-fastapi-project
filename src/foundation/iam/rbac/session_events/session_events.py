from sqlalchemy import event
from sqlalchemy.orm import Session

from src.foundation.iam.rbac.data_scope import get_data_scope_for_write
from src.foundation.iam.rbac.session_events.audit_filler import fill_creator, fill_updater
from src.foundation.iam.rbac.session_events.org_filler import fill_org
from src.foundation.iam.rbac.session_events.tenant_filler import fill_tenant_id
from src.foundation.iam.rbac.tenant_scope import get_tenant_scope_for_write, TenantScope


def fill_instance_fields(instance, tenant_scope: TenantScope) -> None:
    if tenant_scope.skip:
        return

    fill_tenant_id(instance, tenant_scope)
    fill_creator(instance)
    fill_updater(instance)


@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    tenant_scope = get_tenant_scope_for_write()
    data_scope = get_data_scope_for_write()

    for instance in session.new:
        fill_instance_fields(instance, tenant_scope)
        fill_org(instance, data_scope)

    for instance in session.dirty:
        fill_updater(instance)