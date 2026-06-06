"""
部门模型测试
"""

import pytest
from src.models.platform import Dept


def test_dept_model_creation(db_session):
    """测试部门模型创建"""
    dept = Dept(
        name="测试部门",
        code="test_dept",
        sort=1,
        remark="测试用部门",
    )
    
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    
    assert dept.id is not None
    assert dept.name == "测试部门"
    assert dept.code == "test_dept"
    assert dept.sort == 1


def test_dept_to_dict(db_session):
    """测试部门转字典"""
    dept = Dept(
        name="dict_dept",
        code="dict_dept_code",
    )
    
    db_session.add(dept)
    db_session.commit()
    
    dept_dict = dept.to_dict()
    
    assert "name" in dept_dict
    assert "code" in dept_dict
    assert dept_dict["name"] == "dict_dept"
