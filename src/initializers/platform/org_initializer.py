"""
组织初始化器

负责系统组织数据的初始化
"""

from sqlalchemy import select
from src.core.constants import StatusConst
from src.core.log import logger
from src.core.storage import get_db


def init_orgs():
    """
    初始化系统组织

    创建默认的平台级组织结构
    """
    logger.info("开始初始化系统组织...")
    for session in get_db():
        from src.models.platform import Org
        result = session.execute(select(Org))
        orgs = result.scalars().first()
        if not orgs:
            root_org = Org(
                name="总部",
                code="HQ",
                parent_id=None,
                sort=1,
                status=StatusConst.ENABLED,
                creator_id=1
            )
            session.add(root_org)
            session.flush()

            child_orgs = [
                Org(
                    name="技术部",
                    code="TECH",
                    parent_id=root_org.id,
                    sort=1,
                    status=StatusConst.ENABLED,
                    creator_id=1
                ),
                Org(
                    name="产品部",
                    code="PRODUCT",
                    parent_id=root_org.id,
                    sort=2,
                    status=StatusConst.ENABLED,
                    creator_id=1
                ),
                Org(
                    name="运营部",
                    code="OPERATIONS",
                    parent_id=root_org.id,
                    sort=3,
                    status=StatusConst.ENABLED,
                    creator_id=1
                ),
                Org(
                    name="财务部",
                    code="FINANCE",
                    parent_id=root_org.id,
                    sort=4,
                    status=StatusConst.ENABLED,
                    creator_id=1
                ),
                Org(
                    name="人事部",
                    code="HR",
                    parent_id=root_org.id,
                    sort=5,
                    status=StatusConst.ENABLED,
                    creator_id=1
                ),
            ]
            session.add_all(child_orgs)
            session.commit()
            logger.info("系统组织初始化成功 - 组织数量: 6")
        else:
            logger.info("系统组织已存在，跳过初始化")
