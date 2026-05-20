"""
角色管理模块测试
"""

import pytest


class TestRoleList:
    """角色列表接口测试"""

    def test_list_roles_success(self, client, superadmin_user, superadmin_role, auth_headers):
        """测试获取角色列表"""
        response = client.get(
            "/api/v1/roles/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

    def test_list_roles_without_auth(self, client):
        """测试未认证获取角色列表"""
        response = client.get("/api/v1/roles/list")
        assert response.status_code == 401


class TestRoleCreate:
    """创建角色接口测试"""

    def test_create_role_success(self, client, superadmin_user, auth_headers):
        """测试正常创建角色"""
        response = client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={
                "name": "测试角色",
                "remark": "测试用角色"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_system_role_forbidden(self, client, superadmin_user, auth_headers):
        """测试禁止创建系统角色"""
        response = client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={
                "name": "伪装系统角色",
                "remark": "测试",
                "is_system": True
            }
        )
        assert response.status_code == 403


class TestRoleUpdate:
    """更新角色接口测试"""

    def test_update_role_success(self, client, superadmin_user, auth_headers):
        """测试正常更新角色"""
        # 先创建角色
        create_response = client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={
                "name": "待更新角色",
                "remark": "原始备注"
            }
        )
        role_id = create_response.json()["data"]["id"]

        # 更新角色
        response = client.put(
            f"/api/v1/roles/{role_id}",
            headers=auth_headers,
            json={
                "name": "已更新角色",
                "remark": "新备注"
            }
        )
        assert response.status_code == 200

    def test_update_system_role_forbidden(self, client, superadmin_user, superadmin_role, auth_headers):
        """测试禁止更新系统角色"""
        response = client.put(
            f"/api/v1/roles/{superadmin_role.id}",
            headers=auth_headers,
            json={
                "name": "尝试修改系统角色"
            }
        )
        assert response.status_code == 403


class TestRoleDelete:
    """删除角色接口测试"""

    def test_delete_role_success(self, client, superadmin_user, auth_headers):
        """测试正常删除角色"""
        # 先创建角色
        create_response = client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={
                "name": "待删除角色",
                "remark": "测试"
            }
        )
        role_id = create_response.json()["data"]["id"]

        # 删除角色
        response = client.delete(
            f"/api/v1/roles/{role_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_system_role_forbidden(self, client, superadmin_user, superadmin_role, auth_headers):
        """测试禁止删除系统角色"""
        response = client.delete(
            f"/api/v1/roles/{superadmin_role.id}",
            headers=auth_headers
        )
        assert response.status_code == 403


class TestRoleResources:
    """角色资源分配接口测试"""

    def test_assign_resources_to_role(self, client, superadmin_user, auth_headers):
        """测试为角色分配资源"""
        # 先创建角色
        create_response = client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={
                "name": "资源分配测试角色",
                "remark": "测试"
            }
        )
        role_id = create_response.json()["data"]["id"]

        # 分配资源（空列表测试）
        response = client.post(
            f"/api/v1/roles/{role_id}/resources",
            headers=auth_headers,
            json={
                "resource_ids": []
            }
        )
        assert response.status_code == 200

    def test_update_system_role_resources_forbidden(self, client, superadmin_user, superadmin_role, auth_headers):
        """测试禁止修改系统角色资源"""
        response = client.post(
            f"/api/v1/roles/{superadmin_role.id}/resources",
            headers=auth_headers,
            json={
                "resource_ids": [1, 2, 3]
            }
        )
        assert response.status_code == 403
