"""
数据库初始化器

负责数据库表结构的创建
"""

from src.common.core.log import logger
from src.common.core.storage import Base, engine


def init_db():
    """
    创建数据库表结构

    使用 SQLAlchemy 的 Base.metadata.create_all() 根据模型定义
    自动创建所有表（如果不存在）
    """
    logger.info("开始数据库表结构创建...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表结构创建完成")
