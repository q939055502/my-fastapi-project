from src.foundation.iam.rbac.data_scope import DataScope


def _has_column(entity, column_name: str) -> bool:
    return hasattr(entity, column_name)


def fill_org(instance, data_scope: DataScope) -> bool:
    if data_scope.skip or data_scope.dimension_type != 'org':
        return False
    if not _has_column(instance, 'org_id'):
        return False
    if getattr(instance, 'org_id', None) is not None:
        return False

    if data_scope.match_type == 'eq':
        org_id = int(data_scope.dimension_value) if data_scope.dimension_value else None
        if org_id:
            instance.org_id = org_id
            if _has_column(instance, 'org_root_id') and getattr(instance, 'org_root_id', None) is None:
                instance.org_root_id = org_id
            return True
    elif data_scope.match_type == 'in':
        org_ids = data_scope.dimension_value
        if org_ids and isinstance(org_ids, list) and len(org_ids) > 0:
            instance.org_id = org_ids[0]
            if _has_column(instance, 'org_root_id') and getattr(instance, 'org_root_id', None) is None:
                instance.org_root_id = org_ids[0]
            return True

    return False