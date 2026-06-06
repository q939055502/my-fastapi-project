"""
角色模型测试
"""

import pytest
from src.models.platform import Role


def test_role_model_creation(db_session):
    """测试角色模型创建"""
    role = Role(
        name="测试角色",
        remark="测试用角色",
    )
    
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    
    assert role.id is not None
    assert role.name == "测试角色"
    assert role.is_system is False


def test_role_to_dict(db_session):
    """测试角色转字典"""
    role = Role(
        name="dict_role",
    )
    
    db_session.add(role)
    db_session.commit()
    
    role_dict = role.to_dict()
    
    assert "name" in role_dict
    assert role_dict["name"] == "dict_role"
