"""
pytest 配置和共享 fixtures
"""

import sys
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 确保 src 目录在 Python 路径中
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.core.config import settings
from src.models.base import BaseModel
from src.core.storage import get_db


@pytest.fixture(scope="session")
def engine():
    """创建测试数据库引擎"""
    database_url = settings.SQLALCHEMY_DATABASE_URL
    
    if "sqlite" in database_url:
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(database_url)
    
    BaseModel.metadata.create_all(bind=engine)
    yield engine
    BaseModel.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """创建数据库会话"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """创建测试客户端"""
    from src import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "alias": "测试用户",
        "email": "test@example.com",
        "phone": "13800138000",
        "password": "Test123456",
        "gender": 1,
        "is_active": True,
    }


@pytest.fixture
def sample_role_data():
    """示例角色数据"""
    return {
        "name": "测试角色",
        "code": "test_role",
        "remark": "测试用角色",
        "sort": 1,
    }


@pytest.fixture
def sample_dept_data():
    """示例部门数据"""
    return {
        "name": "测试部门",
        "code": "test_dept",
        "sort": 1,
        "remark": "测试用部门",
    }
