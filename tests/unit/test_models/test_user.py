"""
User 模型单元测试

聚焦有实际业务价值的测试：
- 实例方法（业务逻辑）
- 状态判断逻辑
- 模型属性约束
"""

import pytest
from datetime import datetime


class TestUserModelBusinessLogic:
    """User 模型业务逻辑测试"""

    @pytest.mark.unit
    def test_is_active_user_when_active(self, empty_user_model):
        """测试：is_active=1 且未删除时，用户处于激活状态"""
        user = empty_user_model
        user.is_active = True
        user.delete_time = None
        assert user.is_active_user() is True

    @pytest.mark.unit
    def test_is_active_user_when_inactive(self, empty_user_model):
        """测试：is_active=0 时，用户未激活"""
        user = empty_user_model
        user.is_active = False
        user.delete_time = None
        assert user.is_active_user() is False

    @pytest.mark.unit
    def test_is_active_user_when_deleted(self, empty_user_model):
        """测试：delete_time 有值时，用户已删除（软删除）"""
        user = empty_user_model
        user.is_active = True
        user.delete_time = datetime.now()
        assert user.is_active_user() is False

    @pytest.mark.unit
    def test_is_active_user_both_inactive_and_deleted(self, empty_user_model):
        """测试：is_active=0 且 delete_time 有值的边界情况"""
        user = empty_user_model
        user.is_active = False
        user.delete_time = datetime.now()
        assert user.is_active_user() is False

    @pytest.mark.unit
    def test_has_role_when_has_role(self):
        """测试：用户拥有指定角色时返回 True"""
        from src.models.platform import User, Role, RoleSubject
        from unittest.mock import MagicMock

        user = User(id=1)
        role = Role(id=1, name="admin")
        role_subject = RoleSubject(subject_type=0, subject_id=1, role=role)
        user.role_subjects = [role_subject]

        assert user.has_role("admin") is True

    @pytest.mark.unit
    def test_has_role_when_no_role(self):
        """测试：用户没有角色时返回 False"""
        from src.models.platform import User

        user = User(id=1)
        user.role_subjects = []

        assert user.has_role("admin") is False

    @pytest.mark.unit
    def test_has_role_when_role_not_match(self):
        """测试：用户角色不匹配时返回 False"""
        from src.models.platform import User, Role, RoleSubject

        user = User(id=1)
        role = Role(id=1, name="user")
        role_subject = RoleSubject(subject_type=0, subject_id=1, role=role)
        user.role_subjects = [role_subject]

        assert user.has_role("admin") is False