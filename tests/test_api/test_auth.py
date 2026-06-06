"""
认证接口测试
"""

import pytest
from src.models.platform import User
from src.core.security import get_password_hash


def test_login_success(test_client, db_session):
    """测试登录成功"""
    user = User(
        username="login_test",
        email="login@example.com",
        password=get_password_hash("Test123456"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_test",
            "password": "Test123456",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


def test_login_invalid_credentials(test_client):
    """测试登录失败 - 错误凭据"""
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrong_password",
        }
    )
    
    assert response.status_code in [400, 401]


def test_health_check(test_client):
    """测试健康检查接口"""
    response = test_client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_public_version(test_client):
    """测试获取版本信息"""
    response = test_client.get("/api/v1/public/version")
    
    assert response.status_code == 200
    data = response.json()
    assert "version" in data or "data" in data
