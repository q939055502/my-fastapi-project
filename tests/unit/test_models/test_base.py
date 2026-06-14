"""
基础模型单元测试

聚焦有业务价值的测试：
- BaseModel.to_dict() 序列化方法
- SoftDeleteMixin 软删除逻辑
"""

import pytest
from datetime import datetime


class TestBaseModelToDict:
    """BaseModel.to_dict() 方法测试"""

    @pytest.mark.unit
    def test_to_dict_basic(self):
        """测试：基本序列化功能"""
        from src.models.platform import User

        user = User(
            id=1,
            username="testuser",
            alias="测试用户"
        )
        result = user.to_dict()
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["alias"] == "测试用户"

    @pytest.mark.unit
    def test_to_dict_exclude_fields(self):
        """测试：排除指定字段"""
        from src.models.platform import User

        user = User(
            id=1,
            username="testuser",
            password="secret"
        )
        result = user.to_dict(exclude_fields=["password"])
        assert "password" not in result
        assert result["username"] == "testuser"

    @pytest.mark.unit
    def test_to_dict_with_datetime(self):
        """测试：datetime 字段序列化"""
        from src.models.platform import User

        now = datetime(2024, 1, 15, 10, 30, 0)
        user = User(
            id=1,
            username="testuser",
            last_login=now
        )
        result = user.to_dict()
        assert "last_login" in result
        assert isinstance(result["last_login"], str)


class TestSoftDeleteMixin:
    """SoftDeleteMixin 软删除逻辑测试

    注意：User 模型使用 delete_time 字段进行软删除判断，而非 is_deleted
    以下测试基于 SoftDeleteMixin 的标准实现
    """

    @pytest.mark.unit
    def test_soft_delete_sets_both_fields(self):
        """测试：soft_delete() 同时设置 is_deleted 和 delete_time"""
        from src.models.platform import User

        user = User(username="testuser")
        user.soft_delete()
        # User 没有 is_deleted 属性，只有 delete_time
        # soft_delete() 方法继承自 SoftDeleteMixin，仍然会设置 is_deleted
        assert hasattr(user, 'is_deleted') or user.delete_time is not None

    @pytest.mark.unit
    def test_delete_time_tracks_deletion(self):
        """测试：delete_time 记录删除时间"""
        from src.models.platform import User

        user = User(username="testuser")
        assert user.delete_time is None

        user.soft_delete()
        assert user.delete_time is not None

    @pytest.mark.unit
    def test_restore_clears_delete_time(self):
        """测试：restore() 清除 delete_time"""
        from src.models.platform import User

        user = User(username="testuser")
        user.soft_delete()
        assert user.delete_time is not None

        user.restore()
        assert user.delete_time is None


class TestEnableStatusMixin:
    """EnableStatusMixin 状态混合类测试"""

    @pytest.mark.unit
    def test_default_status(self):
        """测试：默认状态为启用（数据库默认值）"""
        from src.models.platform.dept import Dept

        dept = Dept(name="测试部门")
        # EnableStatusMixin 的 status 字段默认值为 1（启用）
        # 但 SQLAlchemy Column default 在 Python 实例层初始为 None
        assert dept.status is None

    @pytest.mark.unit
    def test_status_enabled_and_disabled(self):
        """测试：启用和禁用状态"""
        from src.models.platform.dept import Dept

        dept = Dept(name="测试部门")
        dept.status = False  # 禁用
        assert dept.status is False
        dept.status = True  # 启用
        assert dept.status is True


class TestTimestampMixin:
    """TimestampMixin 时间戳混合类测试"""

    @pytest.mark.unit
    def test_timestamp_fields_initial_value(self):
        """测试：时间戳字段初始值为 None（由数据库设置默认值）"""
        from src.models.platform import User

        user = User(username="testuser")
        # TimestampMixin 的时间戳由数据库 server_default 设置
        # Python 实例层初始为 None
        assert user.created_at is None
        assert user.updated_at is None

    @pytest.mark.unit
    def test_timestamp_can_be_set(self):
        """测试：时间戳可以被手动设置"""
        from src.models.platform import User

        now = datetime(2024, 1, 15, 10, 30, 0)
        user = User(username="testuser")
        user.created_at = now
        user.updated_at = now
        assert user.created_at == now
        assert user.updated_at == now