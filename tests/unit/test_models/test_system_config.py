"""
SystemConfig 模型单元测试

测试配置模型的业务逻辑：
- typed_value 属性（类型化值转换）
"""

import pytest


class TestSystemConfigTypedValue:
    """配置值类型转换测试"""

    @pytest.mark.unit
    def test_typed_value_int(self):
        """测试：int 类型配置值转换"""
        from src.models.platform import SystemConfig

        config = SystemConfig(
            name="测试配置",
            code="test_int",
            value="42",
            config_type="int"
        )
        assert config.typed_value == 42

    @pytest.mark.unit
    def test_typed_value_int_empty(self):
        """测试：int 类型配置值为空"""
        from src.models.platform import SystemConfig

        config = SystemConfig(
            name="测试配置",
            code="test_int_empty",
            value="",
            config_type="int"
        )
        assert config.typed_value == 0

    @pytest.mark.unit
    def test_typed_value_boolean_true(self):
        """测试：boolean 类型配置值为 true"""
        from src.models.platform import SystemConfig

        config1 = SystemConfig(code="test_bool1", value="true", config_type="boolean")
        config2 = SystemConfig(code="test_bool2", value="1", config_type="boolean")
        config3 = SystemConfig(code="test_bool3", value="yes", config_type="boolean")
        
        assert config1.typed_value is True
        assert config2.typed_value is True
        assert config3.typed_value is True

    @pytest.mark.unit
    def test_typed_value_boolean_false(self):
        """测试：boolean 类型配置值为 false"""
        from src.models.platform import SystemConfig

        config1 = SystemConfig(code="test_bool_false", value="false", config_type="boolean")
        config2 = SystemConfig(code="test_bool_0", value="0", config_type="boolean")
        config3 = SystemConfig(code="test_bool_empty", value="", config_type="boolean")
        
        assert config1.typed_value is False
        assert config2.typed_value is False
        assert config3.typed_value is False

    @pytest.mark.unit
    def test_typed_value_json(self):
        """测试：json 类型配置值转换"""
        from src.models.platform import SystemConfig

        config = SystemConfig(
            code="test_json",
            value='{"key": "value", "number": 123}',
            config_type="json"
        )
        result = config.typed_value
        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 123

    @pytest.mark.unit
    def test_typed_value_json_empty(self):
        """测试：json 类型配置值为空"""
        from src.models.platform import SystemConfig

        config = SystemConfig(code="test_json_empty", value="", config_type="json")
        assert config.typed_value == {}

    @pytest.mark.unit
    def test_typed_value_string(self):
        """测试：string 类型配置值（默认）"""
        from src.models.platform import SystemConfig

        config = SystemConfig(code="test_string", value="hello world", config_type="string")
        assert config.typed_value == "hello world"

    @pytest.mark.unit
    def test_typed_value_default_type(self):
        """测试：未指定类型时默认返回字符串"""
        from src.models.platform import SystemConfig

        config = SystemConfig(code="test_default", value="some value", config_type="unknown")
        assert config.typed_value == "some value"