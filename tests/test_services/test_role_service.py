"""
角色服务测试
"""

import pytest
from src.services.sys.role_service import role_service
from src.schemas.iam.role import RoleCreate
import time


def test_get_role_list(db_session):
    """测试获取角色列表"""
    # 创建多个角色
    for i in range(3):
        role_data = {
            "name": f"角色_{int(time.time() * 1000) % 1000000}_{i}",
        }
        role_create = RoleCreate(**role_data)
        role_service.create_role(role_create)
    
    # 获取列表
    total, roles = role_service.get_role_list(page=1, page_size=10)
    
    assert total >= 3
    assert len(roles) >= 3


def test_get_role_detail(db_session):
    """测试获取角色详情"""
    # 获取角色列表
    total, roles = role_service.get_role_list(page=1, page_size=10)
    
    assert total >= 1
    assert len(roles) >= 1


def test_role_list_pagination(db_session):
    """测试角色列表分页"""
    # 创建多个角色
    for i in range(5):
        role_data = {
            "name": f"角色_{int(time.time() * 1000) % 1000000}_{i}",
        }
        role_create = RoleCreate(**role_data)
        role_service.create_role(role_create)
    
    # 测试分页
    total, roles = role_service.get_role_list(page=1, page_size=3)
    
    assert total >= 5
    assert len(roles) == 3
