"""
租户服务测试
"""

import pytest
from src.services.sys.tenant_service import tenant_service
from src.schemas.sys.tenant import TenantUpdate
import time


def test_get_tenant_list(db_session):
    """测试获取租户列表"""
    total, tenants = tenant_service.get_tenant_list(page=1, page_size=10)
    
    assert isinstance(total, int)
    assert isinstance(tenants, list)


def test_get_tenant_detail_not_found(db_session):
    """测试获取不存在的租户"""
    from fastapi import HTTPException
    
    try:
        tenant_service.get_tenant_detail(99999)
        assert False, "应该抛出异常"
    except HTTPException as e:
        assert e.status_code == 404
        assert "租户不存在" in str(e.detail)
