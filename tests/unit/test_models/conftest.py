import pytest
import json
from src.models.platform import User
# 专属夹具：初始化空的 User 模型
@pytest.fixture(scope="function")
def empty_user_model():
    return User()

# 专属夹具：加载模型测试数据（复用根目录的路径夹具）
@pytest.fixture(scope="function")
def user_model_test_data(module_fixtures_dir):
    """加载 fixtures/unit/test_models/user_model_cases.json"""
    file_path = module_fixtures_dir / "user_model_cases.json"
    # 若文件不存在，返回默认空数据（避免报错）
    if not file_path.exists():
        return {"create": [], "update": [], "delete": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)