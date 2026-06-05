"""
用户服务测试
"""

import pytest
from src.services.sys.user_service import user_service
from src.schemas.iam.user import UserCreate, UserUpdate
import time


def test_create_user(db_session):
    """测试创建用户"""
    unique = int(time.time() * 1000) % 1000000
    user_data = {
        "username": f"testuser_{unique}",
        "alias": "测试用户",
        "email": f"test_{unique}@example.com",
        "phone": f"1380013{unique:04d}",
        "password": "Test123456",
        "gender": 1,
    }
    user_create = UserCreate(**user_data)
    result = user_service.create_user(user_create)
    
    assert result is not None


def test_get_user_detail(db_session):
    """测试获取用户详情"""
    unique = int(time.time() * 1000) % 1000000
    user_data = {
        "username": f"testuser_{unique}",
        "email": f"test_{unique}@example.com",
        "password": "Test123456",
    }
    user_create = UserCreate(**user_data)
    result = user_service.create_user(user_create)
    
    # 获取详情
    user_detail = user_service.get_user_detail(result["id"])
    
    assert user_detail is not None
    assert user_detail["username"] == user_data["username"]


def test_get_user_list(db_session):
    """测试获取用户列表"""
    # 创建多个用户
    for i in range(3):
        unique = int(time.time() * 1000) % 1000000 + i
        user_data = {
            "username": f"user{unique}",
            "email": f"user{unique}@example.com",
            "password": "Test123456",
        }
        user_create = UserCreate(**user_data)
        user_service.create_user(user_create)
    
    # 获取列表
    total, users = user_service.get_user_list(page=1, page_size=10)
    
    assert total >= 3
    assert len(users) >= 3
