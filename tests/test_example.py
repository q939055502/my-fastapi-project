"""
测试用例示例模块
"""

from fastapi import status


class TestAuthLogin:
    """登录认证测试"""
    
    def test_login_success(self, client, superadmin_user):
        """测试登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "test_superadmin",
                "password": "qaz123456"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, superadmin_user):
        """测试密码错误"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "test_superadmin",
                "password": "wrong_password"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["code"] == 400
    
    def test_login_user_not_exists(self, client):
        """测试用户不存在"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "qaz123456"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["code"] == 400


class TestUserList:
    """用户列表测试"""
    
    def test_list_users_without_auth(self, client):
        """测试未认证访问"""
        response = client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_users_with_auth(self, client, auth_headers, superadmin_user):
        """测试已认证访问"""
        response = client.get(
            "/api/v1/users/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert len(data["data"]["items"]) >= 1
