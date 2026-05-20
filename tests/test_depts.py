"""
部门管理模块测试
"""

import pytest


class TestDeptList:
    """部门列表接口测试"""

    def test_list_depts_success(self, client, superadmin_user, auth_headers):
        """测试获取部门列表"""
        response = client.get(
            "/api/v1/depts/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_list_depts_without_auth(self, client):
        """测试未认证获取部门列表"""
        response = client.get("/api/v1/depts/list")
        assert response.status_code == 401


class TestDeptCreate:
    """创建部门接口测试"""

    def test_create_dept_success(self, client, superadmin_user, auth_headers):
        """测试正常创建部门"""
        response = client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "测试部门",
                "code": "test_dept",
                "sort": 1,
                "status": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_dept_duplicate_code(self, client, superadmin_user, auth_headers):
        """测试创建重复编码部门"""
        # 先创建一个部门
        client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "部门1",
                "code": "dept_code",
                "sort": 1,
                "status": 1
            }
        )

        # 再次创建同名编码部门
        response = client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "部门2",
                "code": "dept_code",
                "sort": 2,
                "status": 1
            }
        )
        assert response.status_code in [400, 409]

    def test_create_dept_missing_fields(self, client, superadmin_user, auth_headers):
        """测试创建部门缺少必填字段"""
        response = client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "不完整部门"
                # 缺少 code 等必填字段
            }
        )
        assert response.status_code == 422


class TestDeptUpdate:
    """更新部门接口测试"""

    def test_update_dept_success(self, client, superadmin_user, auth_headers):
        """测试正常更新部门"""
        # 先创建部门
        create_response = client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "待更新部门",
                "code": "update_dept",
                "sort": 1,
                "status": 1
            }
        )
        dept_id = create_response.json()["data"]["id"]

        # 更新部门
        response = client.put(
            f"/api/v1/depts/{dept_id}",
            headers=auth_headers,
            json={
                "name": "已更新部门",
                "sort": 10
            }
        )
        assert response.status_code == 200

    def test_update_dept_not_found(self, client, superadmin_user, auth_headers):
        """测试更新不存在的部门"""
        response = client.put(
            "/api/v1/depts/99999",
            headers=auth_headers,
            json={
                "name": "不存在部门"
            }
        )
        assert response.status_code == 404


class TestDeptDelete:
    """删除部门接口测试"""

    def test_delete_dept_success(self, client, superadmin_user, auth_headers):
        """测试正常删除部门（软删除）"""
        # 先创建部门
        create_response = client.post(
            "/api/v1/depts/",
            headers=auth_headers,
            json={
                "name": "待删除部门",
                "code": "delete_dept",
                "sort": 1,
                "status": 1
            }
        )
        dept_id = create_response.json()["data"]["id"]

        # 删除部门
        response = client.delete(
            f"/api/v1/depts/{dept_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_dept_not_found(self, client, superadmin_user, auth_headers):
        """测试删除不存在的部门"""
        response = client.delete(
            "/api/v1/depts/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
