"""删除所有数据库表"""
from src.common.core.storage import Base, engine
from sqlalchemy import text

tables = [
    'dict_data',
    'dict_type',
    'tenant_invite',
    'tenant_member',
    'tenant_usage',
    'tenant_hourly_usage',
    'tenant_oper_log',
    'tenant_config',
    'tenant_dict_data',
    'tenant_dict_type',
    'tenant_plan',
    'tenant_quota',
    'tenant',
    'iam_account_bind',
    'iam_user',
    'iam_dept',
    'iam_dept_closure',
    'iam_role_permission',
    'iam_role_subject',
    'iam_permission',
    'iam_role',
    'system_config',
    'login_log',
    'operation_log',
    'audit_log',
    'file_mapping',
]

with engine.connect() as conn:
    for table in tables:
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            print(f'已删除表: {table}')
        except Exception as e:
            print(f'删除表 {table} 失败: {e}')
    conn.commit()

print('所有表已删除完成')
