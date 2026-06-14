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
# 扩展：按测试模块动态生成数据路径
@pytest.fixture(scope="session")
def fixtures_dir():
    """返回根测试数据目录，供子模块复用"""
    return FIXTURES_DIR

@pytest.fixture(scope="function")
def module_fixtures_dir(request):
    """
    动态返回当前测试模块的专属数据目录
    示例：unit/test_models/test_user.py → fixtures/unit/test_models/
    """
    # 获取当前测试模块的相对路径（如 unit/test_models）
    module_rel_path = Path(request.module.__file__).parent.relative_to(ROOT_DIR / "tests")
    # 拼接专属数据目录（如 fixtures/unit/test_models）
    module_fixture_dir = FIXTURES_DIR / module_rel_path
    # 自动创建目录（避免手动建）
    module_fixture_dir.mkdir(parents=True, exist_ok=True)
    return module_fixture_dir
    
@pytest.fixture(scope="session")
def user_db_fake_data():
    """加载纯模型字段的数据库假数据"""
    file_path = FIXTURES_DIR / "db_fake" / "user.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def user_cases_data():
    """加载数据驱动用例（入参+预期结果）"""
    file_path = FIXTURES_DIR / "test_cases" / "user_cases.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

