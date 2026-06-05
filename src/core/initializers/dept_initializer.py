"""
部门初始化器

负责系统部门数据的初始化
"""

from sqlalchemy import select

from src.core.constants import StatusConst
from src.core.log import logger
from src.core.storage import get_db


def init_depts():
    """
    初始化系统部门

    创建默认的平台级部门结构
    """
    logger.info("开始初始化系统部门...")
    for session in get_db():
        from src.models.system import Dept
        result = session.execute(select(Dept))
        depts = result.scalars().first()
        if not depts:
            root_dept = Dept(
                name="总部",
                parent_id=None,
                sort=1,
                status=StatusConst.ENABLED.value,
                tenant_id=0,
                is_system=True
            )
            session.add(root_dept)
            session.flush()

            child_depts = [
                Dept(
                    name="技术部",
                    parent_id=root_dept.id,
                    sort=1,
                    status=StatusConst.ENABLED.value,
                    tenant_id=0,
                    is_system=True
                ),
                Dept(
                    name="产品部",
                    parent_id=root_dept.id,
                    sort=2,
                    status=StatusConst.ENABLED.value,
                    tenant_id=0,
                    is_system=True
                ),
                Dept(
                    name="运营部",
                    parent_id=root_dept.id,
                    sort=3,
                    status=StatusConst.ENABLED.value,
                    tenant_id=0,
                    is_system=True
                ),
                Dept(
                    name="财务部",
                    parent_id=root_dept.id,
                    sort=4,
                    status=StatusConst.ENABLED.value,
                    tenant_id=0,
                    is_system=True
                ),
                Dept(
                    name="人事部",
                    parent_id=root_dept.id,
                    sort=5,
                    status=StatusConst.ENABLED.value,
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(child_depts)
            session.commit()
            logger.info("系统部门初始化成功 - 部门数量: 6")
        else:
            logger.info("系统部门已存在，跳过初始化")
        break
