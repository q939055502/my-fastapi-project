import json
import pytest
from pathlib import Path

# 全局公共夹具（所有测试通用）
# ===================== 路径统一配置（企业规范：硬编码路径易出错，用动态路径） =====================
# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
# 测试数据目录
FIXTURES_DIR = ROOT_DIR / "fixtures"

# ===================== 全局数据夹具：加载 JSON 测试数据 =====================
@pytest.fixture(scope="session")
def user_raw_data():
    """全局用户测试原始数据，所有模型用例共用"""
    data_path = FIXTURES_DIR / "user_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===================== 可选：空夹具/公共工具（后续扩展用） =====================
@pytest.fixture(scope="function")
def empty_user_instance():
    """空 User 模型实例，供单条用例复用"""
    from app.models.user import User
    return User()