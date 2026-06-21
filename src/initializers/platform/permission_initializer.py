"""
Permission Initializer

Responsible for initializing system API permissions:
- Scan all route modules, collect permission codes from require_permission calls
- Automatically create or update permission records in database
- Provide base data for subsequent role permission assignment

Idempotency guarantee:
- Check if API permission already exists, skip creation if exists
- Repeated execution will not produce duplicate data
"""

from sqlalchemy import func, select

from src.core.log import logger
from src.core.storage import get_db


def init_permissions():
    """
    Initialize system API permissions

    Scan all route modules, collect permission codes, and automatically
    create database permission records.
    """
    logger.info("Initializing system API permissions...")

    _import_routes_for_scan()

    from src.foundation.iam.decorators import REGISTERED_PERMISSIONS

    logger.info(f"Found permission codes: {len(REGISTERED_PERMISSIONS)}")

    for session in get_db():
        from src.models.platform import Permission

        created_count = 0

        for permission_code in REGISTERED_PERMISSIONS:
            try:
                scope, resource, action = permission_code.split(":")
            except ValueError:
                logger.warning(f"Invalid permission code format, skipping: {permission_code}")
                continue

            existing = session.execute(
                select(Permission).where(
                    Permission.resource == resource,
                    Permission.action == action,
                    Permission.applicable_scope == scope,
                    Permission.type == "api",
                )
            ).scalar_one_or_none()

            if not existing:
                permission = Permission(
                    resource=resource,
                    action=action,
                    name=f"{resource}_{action}",
                    type="api",
                    applicable_scope=scope,
                    is_system=True,
                )
                session.add(permission)
                created_count += 1

        if created_count > 0:
            session.commit()
            logger.info(f"System API permissions initialized successfully - created: {created_count}")
        else:
            count_result = session.execute(
                select(func.count(Permission.id)).where(Permission.type == "api")
            )
            permission_count = count_result.scalar()
            logger.info(f"System API permissions already exist, skipping - current count: {permission_count}")
        break


def _import_routes_for_scan():
    """
    Import all route modules to trigger require_permission calls and register permission codes

    Note: Import API modules, not individual endpoint files,
    to ensure all route registrations are executed.
    """
    modules = [
        ("src.foundation.system.api", "v1"),
        ("src.foundation.tenant.api", "v1"),
        ("src.foundation.order.api", "v1"),
        ("src.foundation.iam.api", "v1"),
        ("src.foundation.file.api", "v1"),
    ]

    for module_path, attr in modules:
        try:
            __import__(module_path, fromlist=[attr])
            logger.debug(f"Imported route module: {module_path}.{attr}")
        except Exception as e:
            logger.warning(f"Failed to import route module {module_path}.{attr}: {e}")