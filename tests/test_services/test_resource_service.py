"""
资源服务测试
"""

import pytest
from src.services.sys.resource_service import resource_service
from src.modules.platform.schemas.permission import PermissionCreate, PermissionUpdate
import time


def test_get_resource_list(db_session):
    """测试获取资源列表"""
    total, resources = resource_service.get_resource_list(page=1, page_size=10)
    
    assert isinstance(total, int)
    assert isinstance(resources, list)


def test_get_resource_detail_not_found(db_session):
    """测试获取不存在的资源"""
    from fastapi import HTTPException
    
    try:
        resource_service.get_resource_detail(99999)
        assert False, "应该抛出异常"
    except HTTPException as e:
        assert e.status_code == 404
        assert "资源不存在" in str(e.detail)


def test_get_resource_types(db_session):
    """测试获取资源类型"""
    types = resource_service.get_resource_types()
    
    assert types is not None
    assert isinstance(types, list)
    assert len(types) > 0


def test_create_resource(db_session):
    """测试创建资源"""
    unique = int(time.time() * 1000) % 1000000
    resource_data = {
        "name": f"测试资源_{unique}",
        "code": f"resource_{unique}",
        "type": 1,  # 1-菜单
        "path": f"/test/{unique}",
        "sort": 1,
    }
    resource_create = ResourceCreate(**resource_data)
    result = resource_service.create_resource(resource_create)
    
    assert result is not None
    assert "id" in result


def test_update_resource(db_session):
    """测试更新资源"""
    unique = int(time.time() * 1000) % 1000000
    resource_data = {
        "name": f"测试资源_{unique}",
        "code": f"resource_{unique}",
        "type": 1,
    }
    resource_create = ResourceCreate(**resource_data)
    result = resource_service.create_resource(resource_create)
    
    if result and "id" in result:
        update_data = ResourceUpdate(name="更新后的资源")
        resource_service.update_resource(result["id"], update_data)
        
        resource_detail = resource_service.get_resource_detail(result["id"])
        assert resource_detail["name"] == "更新后的资源"
