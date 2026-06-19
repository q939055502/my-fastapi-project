"""

角色初始化器



负责系统角色的初始化和权限分配


职责:
- 初始化平台级角色体系

- 为超级管理员角色分配所有权
- 为超级管理员用户绑定超级管理员角色


幂等性保证:
- 检查是否已存在角色,若存在则跳过创建
- 检查是否已存在角色-权限关联,若存在则跳过创建
- 检查是否已存在用户-角色关联,若存在则跳过创建
- 重复执行不会产生重复数据

"""



from sqlalchemy import func, select

from src.core.log import logger
from src.core.storage import get_db


def init_roles():

    """

    初始化平台角色体系
    初始化平台角色体系

    创建系统内置平台角色(tenant_id=0, is_system=True):

    1. 平台超级管理: 全平台最高权限,跨所有租户无限制

    2. 平台运营管理�?- 租户全生命周期管理
    3. 平台财务管理�?- 仅账单, 订单, 充值, 续费, 发票, 欠费管理
    4. 平台审核管理�?- 企业资质审核, 资料审核, 内容审核
    5. 平台运维专员 - 日志查看, 系统状态监控, 简单问题排查
    6. 平台客服专员 - 查看租户基础信息, 工单处理, 协助改基础资料

    7. 平台普通用�?- 平台基础用户,仅能查看个人信息和基础功能

    """

    logger.info("开始初始化平台角色...")

    for session in get_db():

        from src.models.platform import (
            Permission,
            Role,
            RolePermission,
            RoleSubject,
            User,
        )



        result = session.execute(select(Role))

        roles = result.scalars().first()



        if not roles:

            # 创建平台角色

            platform_roles = [

                Role(

                    name="平台超级管理",

                    code="platform_super_admin",

                    remark="全平台最高权限,跨所有租户无限制,可管理所有租户, 可操作回收站, 可物理硬删",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(

                    name="平台运营管理",

                    code="platform_operator",

                    remark="租户全生命周期管理,审核租户入驻, 信息修改,查看租户基础信息, 账号数量,冻结违规租户,分配租户套餐, 配置租户套餐",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(

                    name="平台财务管理",

                    code="platform_finance",

                    remark="仅账单, 订单, 充值, 续费, 发票, 欠费管控,无权查看员工业务数据, 无权冻结租户",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(
                    name="平台审核管理",

                    code="platform_auditor",

                    remark="企业资质审核, 资料审核, 内容审核,无任何账号与租户管理权限",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(

                    name="平台运维专员",

                    code="platform_ops",

                    remark="日志查看, 系统状态监控, 简单问题排查,仅查看,无任何修改删除权限",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(

                    name="平台客服专员",

                    code="platform_support",

                    remark="查看租户基础信息, 工单处理, 协助改基础资料,无权查看隐私数据, 无权改权限",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

                Role(

                    name="平台普通用户",

                    code="platform_normal_user",

                    remark="平台基础用户,仅能查看个人信息和基础功能,无管理权限",

                    is_system=True,

                    tenant_id=None,

                    creator_id=1

                ),

            ]

            session.add_all(platform_roles)

            session.flush()



            # 为超级管理员角色分配所有权�?
            superadmin_role_result = session.execute(

                select(Role).where(Role.code == "platform_super_admin")

            )

            superadmin_role = superadmin_role_result.scalars().first()



            if superadmin_role:

                all_permissions_result = session.execute(select(Permission))

                all_permissions = all_permissions_result.scalars().all()



                for permission in all_permissions:

                    # 检查是否已存在关联

                    existing = session.execute(

                        select(RolePermission).where(

                            RolePermission.role_id == superadmin_role.id,

                            RolePermission.permission_id == permission.id

                        )

                    ).first()

                    if not existing:

                        role_perm = RolePermission(

                            role_id=superadmin_role.id,

                            permission_id=permission.id,

                            creator_id=1

                        )

                        session.add(role_perm)



                # 为超级管理员用户绑定超级管理员角色
                superadmin_user = session.execute(

                    select(User).where(User.username == "superadmin")

                ).scalars().first()



                if superadmin_user:

                    # 检查是否已存在关联

                    existing_role_subject = session.execute(

                        select(RoleSubject).where(

                            RoleSubject.subject_id == superadmin_user.id,

                            RoleSubject.subject_type == 0,

                            RoleSubject.role_id == superadmin_role.id

                        )

                    ).first()



                    if not existing_role_subject:

                        role_subject = RoleSubject(

                            subject_id=superadmin_user.id,

                            subject_type=0,

                            role_id=superadmin_role.id,

                            creator_id=1

                        )

                        session.add(role_subject)

                        logger.info(f"已为超级管理员用户分配平台超级管理员角色 - 用户ID: {superadmin_user.id}")



            session.commit()

            logger.info("平台角色初始化成功 - 共创建 7 个平台角色")

        else:

            count_result = session.execute(select(func.count(Role.id)))

            role_count = count_result.scalar()

            logger.info(f"平台角色已存在,跳过创建 - 当前角色数量: {role_count}")



            # 检查并补充超级管理员用户角色关�?
            superadmin_role_result = session.execute(

                select(Role).where(Role.code == "platform_super_admin")

            )

            superadmin_role = superadmin_role_result.scalars().first()



            if superadmin_role:

                superadmin_user = session.execute(

                    select(User).where(User.username == "superadmin")

                ).scalars().first()



                if superadmin_user:

                    existing_association = session.execute(

                        select(RoleSubject).where(

                            RoleSubject.subject_id == superadmin_user.id,

                            RoleSubject.subject_type == 0,

                            RoleSubject.role_id == superadmin_role.id

                        )

                    ).first()



                    if not existing_association:

                        role_subject = RoleSubject(

                            subject_id=superadmin_user.id,

                            subject_type=0,

                            role_id=superadmin_role.id,

                            creator_id=1

                        )

                        session.add(role_subject)

                        session.commit()

                        logger.info("已为超级管理员用户绑定平台超级管理员角色")

        break

