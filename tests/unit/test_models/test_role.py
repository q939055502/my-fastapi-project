"""
Role 模型单元测试

测试角色模型的业务逻辑和关系
"""

import pytest


class TestRoleRelationship:
    """角色关系测试"""

    @pytest.mark.unit
    def test_role_has_permissions(self):
        """测试：角色关联权限"""
        from src.models.platform.rbac import Role, Permission, RolePermission

        role = Role(name="admin", code="admin")
        perm1 = Permission(name="用户管理", resource="user", action="manage", scope="all", type="api", applicable_scope="tenant")
        perm2 = Permission(name="角色管理", resource="role", action="manage", scope="all", type="api", applicable_scope="tenant")

        rp1 = RolePermission(role=role, permission=perm1)
        rp2 = RolePermission(role=role, permission=perm2)

        role.role_permissions = [rp1, rp2]

        assert len(role.role_permissions) == 2
        assert role.role_permissions[0].permission.resource == "user"

    @pytest.mark.unit
    def test_role_without_permissions(self):
        """测试：角色无权限"""
        from src.models.platform.rbac import Role

        role = Role(name="guest", code="guest")
        role.role_permissions = []

        assert len(role.role_permissions) == 0


class TestRoleSubjectRelationship:
    """角色-主体关联测试"""

    @pytest.mark.unit
    def test_role_subject_user_type(self):
        """测试：用户类型的角色主体"""
        from src.models.platform import User, Role, RoleSubject

        user = User(id=1, username="testuser")
        role = Role(id=1, name="admin", code="admin")

        role_subject = RoleSubject(subject_type=0, subject_id=1, role=role)
        user.role_subjects = [role_subject]

        assert user.has_role("admin") is True

    @pytest.mark.unit
    def test_role_subject_no_role(self):
        """测试：用户无角色"""
        from src.models.platform import User

        user = User(id=1, username="testuser")
        user.role_subjects = []

        assert user.has_role("admin") is False

    @pytest.mark.unit
    def test_role_subject_role_not_match(self):
        """测试：角色不匹配"""
        from src.models.platform import User, Role, RoleSubject

        user = User(id=1, username="testuser")
        role = Role(id=1, name="user", code="user")

        role_subject = RoleSubject(subject_type=0, subject_id=1, role=role)
        user.role_subjects = [role_subject]

        assert user.has_role("admin") is False