"""
Pagination Schema 单元测试

测试范围：
- PaginationInfo：分页信息验证
- PaginationResponse：分页响应验证
"""

import pytest


class TestPaginationInfo:
    """PaginationInfo Schema 测试"""

    @pytest.mark.unit
    def test_pagination_info_normal(self):
        """测试：正常分页信息"""
        from src.common.schemas.common.pagination import PaginationInfo
        
        data = {
            "total": 100,
            "page": 1,
            "page_size": 10,
            "total_pages": 10
        }
        
        result = PaginationInfo(**data)
        assert result.total == 100
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 10

    @pytest.mark.unit
    def test_pagination_info_zero_total(self):
        """测试：边界值 - 总记录数为0"""
        from src.common.schemas.common.pagination import PaginationInfo
        
        data = {
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        
        result = PaginationInfo(**data)
        assert result.total == 0
        assert result.total_pages == 0

    @pytest.mark.unit
    def test_pagination_info_large_page_size(self):
        """测试：边界值 - 较大的每页大小"""
        from src.common.schemas.common.pagination import PaginationInfo
        
        data = {
            "total": 10000,
            "page": 1,
            "page_size": 1000,
            "total_pages": 10
        }
        
        result = PaginationInfo(**data)
        assert result.total_pages == 10

    @pytest.mark.unit
    def test_pagination_info_missing_fields(self):
        """测试：异常入参 - 缺少字段"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": 100,
            "page": 1,
            "page_size": 10
            # 缺少 total_pages
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_invalid_type(self):
        """测试：异常入参 - 类型错误"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": "invalid",  # 应为 int
            "page": 1,
            "page_size": 10,
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_negative_page(self):
        """测试：异常入参 - 负数页码"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": 100,
            "page": -1,  # 非法：页码不能为负数
            "page_size": 10,
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_negative_page_size(self):
        """测试：异常入参 - 负数每页大小"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": 100,
            "page": 1,
            "page_size": -10,  # 非法：每页大小不能为负数
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_zero_page_size(self):
        """测试：异常入参 - 每页大小为0"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": 100,
            "page": 1,
            "page_size": 0,  # 非法：每页大小不能为0
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_negative_total(self):
        """测试：异常入参 - 负数总记录数"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": -100,  # 非法：总记录数不能为负数
            "page": 1,
            "page_size": 10,
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_zero_page(self):
        """测试：异常入参 - 页码为0"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": 100,
            "page": 0,  # 非法：页码从1开始
            "page_size": 10,
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)

    @pytest.mark.unit
    def test_pagination_info_none_value(self):
        """测试：异常入参 - None值"""
        from src.common.schemas.common.pagination import PaginationInfo
        from pydantic import ValidationError
        
        data = {
            "total": None,  # 非法：必填字段不能为None
            "page": 1,
            "page_size": 10,
            "total_pages": 10
        }
        
        with pytest.raises(ValidationError):
            PaginationInfo(**data)


class TestPaginationResponse:
    """PaginationResponse Schema 测试"""

    @pytest.mark.unit
    def test_pagination_response_normal(self):
        """测试：正常分页响应"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        
        items = [{"name": "item1"}, {"name": "item2"}]
        pagination = PaginationInfo(total=100, page=1, page_size=10, total_pages=10)
        
        result = PaginationResponse(list=items, pagination=pagination)
        assert len(result.list) == 2
        assert result.pagination.total == 100
        assert result.pagination.page == 1

    @pytest.mark.unit
    def test_pagination_response_empty_list(self):
        """测试：边界值 - 空数据列表"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        
        pagination = PaginationInfo(total=0, page=1, page_size=10, total_pages=0)
        
        result = PaginationResponse(list=[], pagination=pagination)
        assert len(result.list) == 0
        assert result.pagination.total == 0

    @pytest.mark.unit
    def test_pagination_response_with_model_items(self):
        """测试：使用 Pydantic 模型作为列表项"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        from pydantic import BaseModel
        
        class Item(BaseModel):
            id: int
            name: str
        
        items = [Item(id=1, name="test1"), Item(id=2, name="test2")]
        pagination = PaginationInfo(total=2, page=1, page_size=10, total_pages=1)
        
        result = PaginationResponse[Item](list=items, pagination=pagination)
        assert len(result.list) == 2
        assert result.list[0].id == 1
        assert result.list[0].name == "test1"

    @pytest.mark.unit
    def test_pagination_response_with_dict_items(self):
        """测试：使用字典作为列表项"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        
        items = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
        pagination = PaginationInfo(total=2, page=1, page_size=10, total_pages=1)
        
        result = PaginationResponse[dict](list=items, pagination=pagination)
        assert len(result.list) == 2
        assert result.list[0]["id"] == 1
        assert result.list[0]["name"] == "test1"

    @pytest.mark.unit
    def test_pagination_response_with_primitive_items(self):
        """测试：使用基本类型作为列表项"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        
        items = ["item1", "item2", "item3"]
        pagination = PaginationInfo(total=3, page=1, page_size=10, total_pages=1)
        
        result = PaginationResponse[str](list=items, pagination=pagination)
        assert len(result.list) == 3
        assert result.list[0] == "item1"

    @pytest.mark.unit
    def test_pagination_response_with_nested_model(self):
        """测试：使用嵌套模型作为列表项"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        from pydantic import BaseModel
        
        class Address(BaseModel):
            city: str
            street: str
        
        class User(BaseModel):
            id: int
            name: str
            address: Address
        
        items = [
            User(id=1, name="test1", address=Address(city="Beijing", street="Main St")),
            User(id=2, name="test2", address=Address(city="Shanghai", street="Second Ave"))
        ]
        pagination = PaginationInfo(total=2, page=1, page_size=10, total_pages=1)
        
        result = PaginationResponse[User](list=items, pagination=pagination)
        assert len(result.list) == 2
        assert result.list[0].address.city == "Beijing"

    @pytest.mark.unit
    def test_pagination_response_without_type_param(self):
        """测试：不指定类型参数时的泛型使用"""
        from src.common.schemas.common.pagination import PaginationResponse, PaginationInfo
        
        items = [{"name": "item1"}, {"name": "item2"}]
        pagination = PaginationInfo(total=2, page=1, page_size=10, total_pages=1)
        
        result = PaginationResponse(list=items, pagination=pagination)
        assert len(result.list) == 2
        assert result.list[0]["name"] == "item1"