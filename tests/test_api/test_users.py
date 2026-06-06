"""
用户接口测试
"""

import pytest
from src.models.platform import User
from src.core.security import get_password_hash
import time


def test_admin_users_endpoint_requires_permission(test_client, db_session):
    """测试管理员用户接口需要权限"""
    unique = int(time.time() * 1000) % 1000000
    user = User(
        username=f"api_test_{unique}",
        email=f"api_{unique}@example.com",
        password=get_password_hash("Test123456"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "username": user.username,
            "password": "Test123456",
        }
    )
    token = response.json()["data"]["access_token"]
    
    # 普通用户访问管理员接口应该返回 403 或 404
    response = test_client.get(
        "/api/v1/admin/users/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 预期没有权限
    assert response.status_code in [403, 404]
