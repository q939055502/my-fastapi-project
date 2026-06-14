"""
数据库初始化器

负责数据库表结构的创建
"""

from src.common.core.log import logger
from src.common.core.storage import Base, engine

# 必须导入所有模型，否则 create_all() 无法创建对应表
# 注意：这里导入 models 包会自动注册所有模型到 Base.metadata
import src.models  # noqa: F401


def init_db():
    """
    创建数据库表结构

    使用 SQLAlchemy 的 Base.metadata.create_all() 创建所有表
    注意：该函数不会删除已存在的表，仅创建不存在的表
    生产环境应使用 Alembic 进行数据库迁移
    """
    logger.info("开始数据库表结构创建...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表结构创建完成")