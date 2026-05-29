"""
用户模型测试
"""

import pytest
from src.models.iam import User
from src.repositories.sys.user_repository import user_repository


def test_user_model_creation(db_session):
    """测试用户模型创建"""
    user = User(
        username="test_user",
        email="test@example.com",
        password="hashed_password",
        alias="测试用户",
        is_active=True,
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_user_to_dict(db_session):
    """测试用户模型转字典"""
    user = User(
        username="test_dict",
        email="dict@example.com",
        password="hashed_password",
    )
    
    db_session.add(user)
    db_session.commit()
    
    user_dict = user.to_dict()
    
    assert "username" in user_dict
    assert "email" in user_dict
    assert user_dict["username"] == "test_dict"
