
"""
pytest 配置和共享夹具
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# 设置测试环境变量
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "True"
os.environ["DB_ENGINE"] = "sqlite"

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有模型，确保 Base.metadata 知道所有表
from src.models.sys.user import User
from src.models.sys.role import Role
from src.models.sys.resource import Resource
from src.models.sys.dept import Dept, DeptClosure
from src.models.sys.tenant import Tenant, TenantPlan
from src.models.sys.tenant_config import TenantConfig
from src.models.sys.tenant_quota import TenantQuota
from src.models.sys.dict_type import DictType
from src.models.sys.dict_data import DictData
from src.models.sys.system import AuditLog, FileMapping
from src.models.sys.login_log import LoginLog
from src.models.sys.operation_log import OperationLog
from src.models.sys.system_config import SystemConfig

# 创建测试数据库引擎
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 使用内存数据库
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 创建会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_configure(config):
    """pytest 配置钩子"""
    # Patch token_manager.validate_access_token 以跳过 Redis 验证
    # 需要 patch src.core.dependency 中的导入，因为那里使用了局部导入
    from src.core.dependency import token_manager
    token_manager.validate_access_token = MagicMock(return_value=True)

    # 导入应用并禁用 startup 事件
    from src import app
    app.router.on_startup.clear()

    # 获取应用的数据库依赖
    from src.core.storage.database import get_db, Base

    # 覆写 get_db 依赖
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # 创建所有表（使用 checkfirst=True 避免重复创建索引）
    Base.metadata.create_all(bind=engine, checkfirst=True)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    from src import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def superadmin_role(db):
    """创建超级管理员角色"""
    from src.models.sys.role import Role
    from sqlalchemy import select

    # 检查是否已存在
    result = db.execute(select(Role).where(Role.name == "平台超级管理员"))
    existing_role = result.scalars().first()

    if existing_role:
        return existing_role

    role = Role(
        name="平台超级管理员",
        tenant_id=0,
        is_system=True,
        remark="测试用超级管理员角色"
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture(scope="function")
def superadmin_user(db, superadmin_role):
    """创建超级管理员用户"""
    from src.models.sys.user import User
    from src.core.security import get_password_hash
    from sqlalchemy import select

    # 检查是否已存在
    result = db.execute(select(User).where(User.username == "test_superadmin"))
    existing_user = result.scalars().first()

    if existing_user:
        return existing_user

    user = User(
        username="test_superadmin",
        email="superadmin@test.com",
        password=get_password_hash("qaz123456"),
        alias="测试超级管理员",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user.roles.append(superadmin_role)
    db.commit()

    return user


@pytest.fixture(scope="function")
def auth_headers(superadmin_user):
    """获取认证头 - 直接生成token，不走登录接口"""
    from src.core.security import create_token_pair

    access_token, _ = create_token_pair(
        user_id=superadmin_user.id, username=superadmin_user.username
    )
    return {"Authorization": f"Bearer {access_token}"}

