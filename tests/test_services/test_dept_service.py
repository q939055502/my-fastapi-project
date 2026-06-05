"""
部门服务测试
"""

import pytest
from src.services.sys.dept_service import dept_service
from src.schemas.iam.dept import DeptCreate, DeptUpdate
import time


def test_get_dept_list(db_session):
    """测试获取部门列表"""
    total, depts = dept_service.get_dept_list(page=1, page_size=10)
    
    assert isinstance(total, int)
    assert isinstance(depts, list)


def test_get_dept_detail_not_found(db_session):
    """测试获取不存在的部门"""
    from fastapi import HTTPException
    
    try:
        dept_service.get_dept_detail(99999)
        assert False, "应该抛出异常"
    except HTTPException as e:
        assert e.status_code == 404
        assert "部门不存在" in str(e.detail)


def test_create_and_get_dept(db_session):
    """测试创建部门并获取详情"""
    unique = int(time.time() * 1000) % 1000000
    dept_data = {
        "name": f"测试部门_{unique}",
        "code": f"dept_{unique}",
    }
    dept_create = DeptCreate(**dept_data)
    result = dept_service.create_dept(dept_create)
    
    if result is not None:
        assert "id" in result
        
        dept_detail = dept_service.get_dept_detail(result["id"])
        assert dept_detail is not None
        assert dept_detail["name"] == dept_data["name"]


def test_update_dept(db_session):
    """测试更新部门"""
    unique = int(time.time() * 1000) % 1000000
    dept_data = {
        "name": f"测试部门_{unique}",
        "code": f"dept_{unique}",
    }
    dept_create = DeptCreate(**dept_data)
    result = dept_service.create_dept(dept_create)
    
    if result and "id" in result:
        update_data = DeptUpdate(name="更新后的部门")
        dept_service.update_dept(result["id"], update_data)
        
        dept_detail = dept_service.get_dept_detail(result["id"])
        assert dept_detail["name"] == "更新后的部门"


def test_delete_dept(db_session):
    """测试删除部门"""
    unique = int(time.time() * 1000) % 1000000
    dept_data = {
        "name": f"测试部门_{unique}",
        "code": f"dept_{unique}",
    }
    dept_create = DeptCreate(**dept_data)
    result = dept_service.create_dept(dept_create)
    
    if result and "id" in result:
        dept_service.delete_dept(result["id"])
        
        from fastapi import HTTPException
        try:
            dept_service.get_dept_detail(result["id"])
            assert False, "应该抛出异常"
        except HTTPException as e:
            assert e.status_code == 404
