"""
字典初始化器

负责系统字典数据的初始化
"""

from sqlalchemy import func, select
from src.common.core.constants import StatusConst
from src.common.core.log import logger
from src.common.core.storage import get_db


def init_dict():
    """
    初始化系统字典数据

    创建系统级字典类型和字典数据，用于前端展示下拉选项等场景
    """
    logger.info("开始初始化系统字典...")
    for session in get_db():
        from src.models.platform import DictData, DictType
        result = session.execute(select(DictType))
        dict_types = result.scalars().first()
        if not dict_types:
            dict_types_data = [
                DictType(
                    name="系统状态",
                    code="sys_status",
                    sort=1,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="登录状态",
                    code="login_status",
                    sort=2,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="租户状态",
                    code="tenant_status",
                    sort=3,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="权限类型",
                    code="permission_type",
                    sort=4,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="业务场景",
                    code="scene",
                    sort=5,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="成员入驻类型",
                    code="member_join_type",
                    sort=6,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="审核状态",
                    code="audit_status",
                    sort=7,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="房屋状态",
                    code="house_status",
                    sort=8,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="鉴定类型",
                    code="identification_type",
                    sort=9,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
                DictType(
                    name="鉴定状态",
                    code="identification_status",
                    sort=10,
                    status=StatusConst.ENABLED.value,
                    is_system=True
                ),
            ]
            session.add_all(dict_types_data)
            session.flush()

            sys_status_type = session.execute(
                select(DictType).where(DictType.code == "sys_status")
            ).scalars().first()
            login_status_type = session.execute(
                select(DictType).where(DictType.code == "login_status")
            ).scalars().first()
            tenant_status_type = session.execute(
                select(DictType).where(DictType.code == "tenant_status")
            ).scalars().first()
            permission_type = session.execute(
                select(DictType).where(DictType.code == "permission_type")
            ).scalars().first()
            scene_type = session.execute(
                select(DictType).where(DictType.code == "scene")
            ).scalars().first()
            member_join_type = session.execute(
                select(DictType).where(DictType.code == "member_join_type")
            ).scalars().first()
            audit_status_type = session.execute(
                select(DictType).where(DictType.code == "audit_status")
            ).scalars().first()
            house_status_type = session.execute(
                select(DictType).where(DictType.code == "house_status")
            ).scalars().first()
            identification_type = session.execute(
                select(DictType).where(DictType.code == "identification_type")
            ).scalars().first()
            identification_status_type = session.execute(
                select(DictType).where(DictType.code == "identification_status")
            ).scalars().first()

            dict_datas = []

            if sys_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=sys_status_type.id,
                        label="启用",
                        value=1,
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=sys_status_type.id,
                        label="禁用",
                        value=0,
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if login_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=login_status_type.id,
                        label="成功",
                        value=1,
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=login_status_type.id,
                        label="失败",
                        value=0,
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if tenant_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=tenant_status_type.id,
                        label="正常",
                        value="active",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=tenant_status_type.id,
                        label="暂停",
                        value="suspended",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=tenant_status_type.id,
                        label="试用",
                        value="trial",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=tenant_status_type.id,
                        label="过期",
                        value="expired",
                        sort=4,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if permission_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=permission_type.id,
                        label="菜单",
                        value="menu",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=permission_type.id,
                        label="按钮",
                        value="button",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=permission_type.id,
                        label="接口",
                        value="api",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if scene_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=scene_type.id,
                        label="管理后台",
                        value="admin",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=scene_type.id,
                        label="移动端",
                        value="app",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=scene_type.id,
                        label="商户端",
                        value="merchant",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if member_join_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=member_join_type.id,
                        label="定向邀请",
                        value="private",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=member_join_type.id,
                        label="公开链接加入",
                        value="public",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=member_join_type.id,
                        label="用户自助申请",
                        value="apply",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if audit_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=audit_status_type.id,
                        label="待审核",
                        value=0,
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=audit_status_type.id,
                        label="已通过",
                        value=1,
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=audit_status_type.id,
                        label="已拒绝",
                        value=2,
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if house_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=house_status_type.id,
                        label="正常",
                        value="normal",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=house_status_type.id,
                        label="损坏",
                        value="damaged",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=house_status_type.id,
                        label="危险",
                        value="dangerous",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if identification_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=identification_type.id,
                        label="初始鉴定",
                        value="initial",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=identification_type.id,
                        label="常规鉴定",
                        value="routine",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=identification_type.id,
                        label="专项鉴定",
                        value="special",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            if identification_status_type:
                dict_datas.extend([
                    DictData(
                        dict_type_id=identification_status_type.id,
                        label="待鉴定",
                        value="pending",
                        sort=1,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=identification_status_type.id,
                        label="鉴定中",
                        value="in_progress",
                        sort=2,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                    DictData(
                        dict_type_id=identification_status_type.id,
                        label="已完成",
                        value="completed",
                        sort=3,
                        status=StatusConst.ENABLED.value,
                        is_system=True
                    ),
                ])

            session.add_all(dict_datas)
            session.commit()
            logger.info(f"系统字典初始化成功 - 字典类型: 10, 字典数据: {len(dict_datas)}")
        else:
            type_count = session.execute(select(func.count(DictType.id))).scalar()
            data_count = session.execute(select(func.count(DictData.id))).scalar()
            logger.info(f"系统字典已存在，跳过初始化 - 字典类型: {type_count}, 字典数据: {data_count}")
        break
