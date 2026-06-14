"""
Permission 模型单元测试

测试权限模型的业务逻辑：
- permission_code 属性（生成权限编码）
"""

import pytest


class TestPermissionCode:
    """权限编码生成测试"""

    @pytest.mark.unit
    def test_permission_code_generation(self):
        """测试：生成标准权限编码"""
        from src.models.platform.rbac import Permission

        perm = Permission(
            name="用户管理",
            resource="user",
            action="manage",
            scope="all",
            type="api",
            applicable_scope="tenant"
        )
        assert perm.permission_code == "user:manage:all"

    @pytest.mark.unit
    def test_permission_code_with_different_scope(self):
        """测试：不同数据范围的权限编码"""
        from src.models.platform.rbac import Permission

        perm1 = Permission(resource="user", action="read", scope="self")
        perm2 = Permission(resource="user", action="read", scope="dept")
        perm3 = Permission(resource="user", action="read", scope="all")

        assert perm1.permission_code == "user:read:self"
        assert perm2.permission_code == "user:read:dept"
        assert perm3.permission_code == "user:read:all"

    @pytest.mark.unit
    def test_permission_code_empty_resource_action(self):
        """测试：空资源或操作的边界情况"""
        from src.models.platform.rbac import Permission

        perm = Permission(resource="", action="", scope="all")
        assert perm.permission_code == "::all"