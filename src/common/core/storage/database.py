"""SQLAlchemy 数据库连接管理"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from src.common.core.config import settings

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if not settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def close_db():
    """关闭数据库连接"""
    engine.dispose()
