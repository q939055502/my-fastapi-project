"""
租户管理模块测试（平台管理员接口）
"""

import pytest


class TestTenantList:
    """租户列表接口测试"""

    def test_list_tenants_success(self, client, superadmin_user, auth_headers):
        """测试获取租户列表"""
        response = client.get(
            "/api/v1/admin/tenants/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_list_tenants_without_auth(self, client):
        """测试未认证获取租户列表"""
        response = client.get("/api/v1/admin/tenants/list")
        assert response.status_code == 401


class TestTenantCreate:
    """创建租户接口测试"""

    def test_create_tenant_success(self, client, superadmin_user, auth_headers):
        """测试正常创建租户"""
        response = client.post(
            "/api/v1/admin/tenants/",
            headers=auth_headers,
            json={
                "name": "测试租户",
                "code": "test_tenant_new",
                "plan_id": 1,
                "owner_user_id": 1,
                "status": "active"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_tenant_duplicate_code(self, client, superadmin_user, auth_headers):
        """测试创建重复编码租户"""
        # 先创建一个租户
        client.post(
            "/api/v1/admin/tenants/",
            headers=auth_headers,
            json={
                "name": "租户1",
                "code": "dup_tenant",
                "plan_id": 1,
                "owner_user_id": 1,
                "status": "active"
            }
        )

        # 再次创建同名编码租户
        response = client.post(
            "/api/v1/admin/tenants/",
            headers=auth_headers,
            json={
                "name": "租户2",
                "code": "dup_tenant",
                "plan_id": 1,
                "owner_user_id": 1,
                "status": "active"
            }
        )
        assert response.status_code in [400, 409]


class TestTenantUpdate:
    """更新租户接口测试"""

    def test_update_tenant_success(self, client, superadmin_user, auth_headers):
        """测试正常更新租户"""
        # 先创建租户
        create_response = client.post(
            "/api/v1/admin/tenants/",
            headers=auth_headers,
            json={
                "name": "待更新租户",
                "code": "update_tenant",
                "plan_id": 1,
                "owner_user_id": 1,
                "status": "active"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 更新租户
        response = client.put(
            f"/api/v1/admin/tenants/{tenant_id}",
            headers=auth_headers,
            json={
                "name": "已更新租户",
                "status": "suspended"
            }
        )
        assert response.status_code == 200

    def test_update_tenant_not_found(self, client, superadmin_user, auth_headers):
        """测试更新不存在的租户"""
        response = client.put(
            "/api/v1/admin/tenants/99999",
            headers=auth_headers,
            json={
                "name": "不存在租户"
            }
        )
        assert response.status_code == 404


class TestTenantDelete:
    """删除租户接口测试"""

    def test_delete_tenant_success(self, client, superadmin_user, auth_headers):
        """测试正常删除租户（软删除）"""
        # 先创建租户
        create_response = client.post(
            "/api/v1/admin/tenants/",
            headers=auth_headers,
            json={
                "name": "待删除租户",
                "code": "delete_tenant",
                "plan_id": 1,
                "owner_user_id": 1,
                "status": "active"
            }
        )
        tenant_id = create_response.json()["data"]["id"]

        # 删除租户
        response = client.delete(
            f"/api/v1/admin/tenants/{tenant_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_tenant_not_found(self, client, superadmin_user, auth_headers):
        """测试删除不存在的租户"""
        response = client.delete(
            "/api/v1/admin/tenants/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
