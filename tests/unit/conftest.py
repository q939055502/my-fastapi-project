# 专门放单元测试通用的 Mock
import pytest
from unittest.mock import MagicMock

@pytest.fixture(scope="function")
def mock_db_session():
    """单元测试专用：模拟数据库会话"""
    sess = MagicMock()
    sess.query = MagicMock(return_value=sess)
    sess.filter = MagicMock(return_value=sess)
    sess.first = MagicMock(return_value=None)
    sess.add = MagicMock()
    sess.commit = MagicMock()
    return sess