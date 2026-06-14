# tests/test_tenant_model.py
import pytest
from datetime import datetime, timedelta, UTC
from src.models.tenant.tenant import Tenant

class TestTenantModel:
    """租户模型业务逻辑测试"""
    
    def test_is_trial_period_returns_false_when_no_trial_dates(self):
        """无试用日期时返回False"""
        tenant = Tenant(trial_start_date=None, trial_end_date=None)
        assert tenant.is_trial_period() is False
    
    def test_is_trial_period_returns_true_when_within_trial(self):
        """在试用期内返回True"""
        tenant = Tenant(
            trial_start_date=datetime.now(UTC) - timedelta(days=1),
            trial_end_date=datetime.now(UTC) + timedelta(days=1)
        )
        assert tenant.is_trial_period() is True
    
    def test_is_trial_period_returns_false_when_trial_expired(self):
        """试用期已过返回False"""
        tenant = Tenant(
            trial_start_date=datetime.now(UTC) - timedelta(days=10),
            trial_end_date=datetime.now(UTC) - timedelta(days=1)
        )
        assert tenant.is_trial_period() is False