"""
Tenant 模型单元测试

测试租户模型的业务逻辑：
- is_trial_period() 判断试用期
- is_active_tenant() 判断活跃状态
"""

import pytest
from datetime import datetime, UTC, timedelta


class TestTenantIsTrialPeriod:
    """租户试用期判断测试"""

    @pytest.mark.unit
    def test_is_trial_period_during_trial(self):
        """测试：在试用期内返回 True"""
        from src.models.tenant import Tenant

        now = datetime.now(UTC)
        tenant = Tenant(
            name="测试租户",
            code="test_tenant",
            owner_user_id=1,
            trial_start_date=now - timedelta(days=10),
            trial_end_date=now + timedelta(days=10)
        )
        assert tenant.is_trial_period() is True

    @pytest.mark.unit
    def test_is_trial_period_before_trial(self):
        """测试：试用期开始前返回 False"""
        from src.models.tenant import Tenant

        now = datetime.now(UTC)
        tenant = Tenant(
            name="测试租户",
            code="test_tenant",
            owner_user_id=1,
            trial_start_date=now + timedelta(days=10),
            trial_end_date=now + timedelta(days=30)
        )
        assert tenant.is_trial_period() is False

    @pytest.mark.unit
    def test_is_trial_period_after_trial(self):
        """测试：试用期结束后返回 False"""
        from src.models.tenant import Tenant

        now = datetime.now(UTC)
        tenant = Tenant(
            name="测试租户",
            code="test_tenant",
            owner_user_id=1,
            trial_start_date=now - timedelta(days=30),
            trial_end_date=now - timedelta(days=10)
        )
        assert tenant.is_trial_period() is False

    @pytest.mark.unit
    def test_is_trial_period_no_trial_dates(self):
        """测试：未设置试用日期返回 False"""
        from src.models.tenant import Tenant

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.trial_start_date = None
        tenant.trial_end_date = None
        assert tenant.is_trial_period() is False


class TestTenantIsActive:
    """租户活跃状态判断测试"""

    @pytest.mark.unit
    def test_is_active_tenant_with_valid_quota(self):
        """测试：状态正常且配额有效"""
        from src.models.tenant import Tenant, TenantQuota

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.status = "active"
        tenant.delete_time = None
        
        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) + timedelta(days=30)
        tenant.quota = quota
        
        assert tenant.is_active_tenant() is True

    @pytest.mark.unit
    def test_is_active_tenant_inactive_status(self):
        """测试：状态非 active"""
        from src.models.tenant import Tenant

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.status = "inactive"
        tenant.delete_time = None
        
        assert tenant.is_active_tenant() is False

    @pytest.mark.unit
    def test_is_active_tenant_deleted(self):
        """测试：已删除的租户"""
        from src.models.tenant import Tenant

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.status = "active"
        tenant.delete_time = datetime.now(UTC)
        
        assert tenant.is_active_tenant() is False

    @pytest.mark.unit
    def test_is_active_tenant_no_quota(self):
        """测试：无配额但状态正常"""
        from src.models.tenant import Tenant

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.status = "active"
        tenant.delete_time = None
        tenant.quota = None
        
        assert tenant.is_active_tenant() is True

    @pytest.mark.unit
    def test_is_active_tenant_expired_quota(self):
        """测试：配额已过期"""
        from src.models.tenant import Tenant, TenantQuota

        tenant = Tenant(name="测试租户", code="test_tenant", owner_user_id=1)
        tenant.status = "active"
        tenant.delete_time = None
        
        quota = TenantQuota()
        quota.valid_until = datetime.now(UTC) - timedelta(days=10)
        tenant.quota = quota
        
        assert tenant.is_active_tenant() is False