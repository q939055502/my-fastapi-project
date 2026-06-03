
"""
全局常量配置
存放系统级、通用的固定常量，避免硬编码

职责划分：
- config.py: 应用配置（APP_TITLE、数据库连接、JWT配置等，可通过 .env 覆盖）
- constants.py: 程序固定常量（状态码、角色名称、正则表达式等）

注意：配置项不应放在此文件！
"""

# ========== 环境常量 ==========
ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"
ENV_PRODUCTION = "production"


# ========== 业务状态常量 ==========
# 用于表示启用/禁用的通用状态（Dept、Resource、DictType、DictData、TenantPlan、SystemConfig 等模型使用）
STATUS_ENABLED = 1
STATUS_DISABLED = 0

# ========== 登录日志状态常量 ==========
LOGIN_STATUS_SUCCESS = 1
LOGIN_STATUS_FAILED = 0

# ========== 租户状态常量 ==========
TENANT_STATUS_ACTIVE = "active"
TENANT_STATUS_SUSPENDED = "suspended"
TENANT_STATUS_TRIAL = "trial"
TENANT_STATUS_EXPIRED = "expired"


# ========== 资源类型常量 ==========
RESOURCE_TYPE_MENU = 1
RESOURCE_TYPE_API = 2
RESOURCE_TYPE_BUTTON = 3


# ========== 场景常量 ==========
SCENE_ADMIN = "admin"
SCENE_APP = "app"
SCENE_MERCHANT = "merchant"


# ========== 角色常量 ==========
SUPER_ADMIN_ID = 1

ROLE_PLATFORM_SUPER_ADMIN = "平台超级管理员"
ROLE_PLATFORM_OPERATOR = "平台运营管理员"
ROLE_PLATFORM_FINANCE = "平台财务管理员"
ROLE_PLATFORM_AUDITOR = "平台审核管理员"
ROLE_PLATFORM_SUPPORT = "平台运维专员"
ROLE_PLATFORM_CUSTOMER_SERVICE = "平台客服专员"
ROLE_PLATFORM_NORMAL_USER = "平台普通用户"

SYSTEM_ROLE_NAMES = [
    ROLE_PLATFORM_SUPER_ADMIN,
    ROLE_PLATFORM_OPERATOR,
    ROLE_PLATFORM_FINANCE,
    ROLE_PLATFORM_AUDITOR,
    ROLE_PLATFORM_SUPPORT,
    ROLE_PLATFORM_CUSTOMER_SERVICE,
    ROLE_PLATFORM_NORMAL_USER,
]


# ========== 正则表达式常量 ==========
PHONE_REGEX = r"^1[3-9]\d{9}$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
ID_CARD_REGEX = r"^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$"
PASSWORD_STRONG_REGEX = r"^(?=.*[a-zA-Z])(?=.*\d).{6,}$|^(?=.*[a-z])(?=.*[A-Z]).{6,}$"
USERNAME_REGEX = r"^[a-zA-Z0-9_]{4,20}$"
HOUSE_CODE_REGEX = r"^HJ\d{8}$"


# ========== 分页常量 ==========
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


# ========== 文件扩展名常量 ==========
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}
ALLOWED_DOC_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "wmv", "flv"}


# ========== 文件大小常量 ==========
MAX_FILE_SIZE_IMAGE = 10 * 1024 * 1024
MAX_FILE_SIZE_DOC = 50 * 1024 * 1024
MAX_FILE_SIZE_VIDEO = 500 * 1024 * 1024


# ========== 存储路径常量 ==========
STORAGE_PATH_AVATAR = "avatars"
STORAGE_PATH_HOUSE = "houses"
STORAGE_PATH_REPORT = "reports"
STORAGE_PATH_TEMP = "temp"


# ========== 房屋状态常量 ==========
HOUSE_STATUS_NORMAL = "normal"
HOUSE_STATUS_DAMAGED = "damaged"
HOUSE_STATUS_DANGEROUS = "dangerous"


# ========== 鉴定类型常量 ==========
IDENTIFICATION_TYPE_INITIAL = "initial"
IDENTIFICATION_TYPE_ROUTINE = "routine"
IDENTIFICATION_TYPE_SPECIAL = "special"


# ========== 鉴定状态常量 ==========
IDENTIFICATION_STATUS_PENDING = "pending"
IDENTIFICATION_STATUS_IN_PROGRESS = "in_progress"
IDENTIFICATION_STATUS_COMPLETED = "completed"


# ========== 编码常量 ==========
ENCODING_UTF8 = "utf-8"
ENCODING_GBK = "gbk"


# ========== 其他常量 ==========
DEFAULT_TIMEZONE = "Asia/Shanghai"
EMPTY_VALUES = (None, "", [], {}, set())
