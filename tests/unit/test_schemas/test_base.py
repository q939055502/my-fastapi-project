"""
BaseSchema 单元测试

测试范围：
- filter_system_fields 方法：过滤系统字段逻辑
- SYSTEM_FIELDS 常量
"""

import pytest


class TestSystemFields:
    """SYSTEM_FIELDS 常量测试"""

    @pytest.mark.unit
    def test_system_fields_contains_expected_fields(self):
        """测试：SYSTEM_FIELDS 包含预期的系统字段"""
        from src.common.schemas.base import SYSTEM_FIELDS
        
        expected_fields = {"id", "uuid", "delete_time", "is_system", "created_at", "updated_at"}
        assert SYSTEM_FIELDS == expected_fields


class TestFilterSystemFields:
    """filter_system_fields 方法测试"""

    @pytest.mark.unit
    def test_filter_system_fields_normal_data(self):
        """测试：正常数据过滤系统字段"""
        from src.common.schemas.base import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
        
        data = {
            "id": 1,
            "uuid": "test-uuid",
            "name": "test",
            "email": "test@example.com",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-02"
        }
        
        result = TestSchema.model_validate(data)
        assert result.name == "test"
        assert result.email == "test@example.com"

    @pytest.mark.unit
    def test_filter_system_fields_all_system(self):
        """测试：只包含系统字段的数据应被过滤为空"""
        from src.common.schemas.base import BaseSchema
        
        class EmptySchema(BaseSchema):
            pass
        
        data = {
            "id": 1,
            "uuid": "test-uuid",
            "created_at": "2024-01-01"
        }
        
        result = EmptySchema.model_validate(data)
        assert result.model_dump() == {}

    @pytest.mark.unit
    def test_filter_system_fields_non_dict_input(self):
        """测试：非字典输入不被修改"""
        from src.common.schemas.base import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
        
        # 测试非字典输入
        result = TestSchema.model_validate({"name": "test"})
        assert result.name == "test"

    @pytest.mark.unit
    def test_filter_system_fields_empty_dict(self):
        """测试：空字典输入"""
        from src.common.schemas.base import BaseSchema
        
        class EmptySchema(BaseSchema):
            pass
        
        result = EmptySchema.model_validate({})
        assert result.model_dump() == {}

    @pytest.mark.unit
    def test_filter_system_fields_extra_forbid(self):
        """测试：extra=forbid 禁止额外字段"""
        from src.common.schemas.base import BaseSchema
        from pydantic import ValidationError
        
        class StrictSchema(BaseSchema):
            name: str
        
        with pytest.raises(ValidationError):
            StrictSchema.model_validate({"name": "test", "extra_field": "value"})