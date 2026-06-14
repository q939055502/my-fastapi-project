"""
TenantQuota 模型单元测试

测试租户配额模型的业务逻辑：
- is_valid() 判断配额是否有效
"""

import pytest
from datetime import datetime, UTC, timedelta


class TestTenantQuotaIsValid:
    """租户配额有效性测试"""

    @pytest.mark.unit
    def test_quota_valid_with_future_expiry(self):
        """测试：配额有效且未过期"""
        from src.models.tenant import TenantQuota

        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) + timedelta(days=30)
        quota.delete_time = None
        
        assert quota.is_valid() is True

    @pytest.mark.unit
    def test_quota_valid_no_expiry(self):
        """测试：无过期时间限制"""
        from src.models.tenant import TenantQuota

        quota = TenantQuota()
        quota.valid_until = None
        quota.delete_time = None
        
        assert quota.is_valid() is True

    @pytest.mark.unit
    def test_quota_expired(self):
        """测试：配额已过期"""
        from src.models.tenant import TenantQuota

        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) - timedelta(days=10)
        quota.delete_time = None
        
        assert quota.is_valid() is False

    @pytest.mark.unit
    def test_quota_deleted(self):
        """测试：已删除的配额"""
        from src.models.tenant import TenantQuota

        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) + timedelta(days=30)
        quota.delete_time = datetime.now(UTC)
        
        assert quota.is_valid() is False

    @pytest.mark.unit
    def test_quota_deleted_and_expired(self):
        """测试：已删除且已过期"""
        from src.models.tenant import TenantQuota

        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) - timedelta(days=10)
        quota.delete_time = datetime.now(UTC)
        
        assert quota.is_valid() is False