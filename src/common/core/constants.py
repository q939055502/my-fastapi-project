"""
全局常量配置
存放系统级、通用的固定常量，避免硬编码

职责划分：
- config.py: 应用配置（支持环境变量覆盖）
- constants.py: 程序固定常量（真正固定不变的值，不支持配置覆盖）

常量分类：
- 业务常量：可存入数据库字典表，暴露给前端管理员
- 技术常量：仅后端使用的固定值
"""

from dataclasses import dataclass


# ========== 基础结构体 ==========
@dataclass(frozen=True)
class DictItem:
    """字典项结构体 - 用于封装业务常量值"""
    value: int | str    # 数据库存的值
    label: str          # 前端展示中文
    sort: int = 0       # 排序字段，默认0


# #############################################################################
# 第一部分：业务常量（可存入数据库字典表，暴露给前端管理员）
# #############################################################################

# ========== 通用状态常量 ==========
class StatusConst:
    """通用启用/禁用状态"""
    ENABLED = DictItem(value=1, label="启用", sort=1)
    DISABLED = DictItem(value=0, label="禁用", sort=2)


# ========== 登录日志状态 ==========
class LoginStatusConst:
    """登录状态"""
    SUCCESS = DictItem(value=1, label="成功", sort=1)
    FAILED = DictItem(value=0, label="失败", sort=2)


# ========== 租户状态 ==========
class TenantStatusConst:
    """租户状态"""
    ACTIVE = DictItem(value="active", label="正常", sort=1)
    SUSPENDED = DictItem(value="suspended", label="暂停", sort=2)
    TRIAL = DictItem(value="trial", label="试用", sort=3)
    EXPIRED = DictItem(value="expired", label="过期", sort=4)


# ========== 权限/资源类型 ==========
class PermissionTypeConst:
    """权限/资源类型"""
    MENU = DictItem(value="menu", label="菜单", sort=1)
    BUTTON = DictItem(value="button", label="按钮", sort=2)
    API = DictItem(value="api", label="接口", sort=3)


# ========== 数据范围 ==========
class ScopeConst:
    """数据范围"""
    SELF = DictItem(value="self", label="仅自己", sort=1)
    OWN = DictItem(value="own", label="自己创建", sort=2)
    DEPT = DictItem(value="dept", label="本部门", sort=3)
    DEPT_ALL = DictItem(value="dept_all", label="部门及子部门", sort=4)
    ALL = DictItem(value="all", label="全部数据", sort=5)


# ========== 资源类型 ==========
class ResourceConst:
    """资源类型"""
    # 平台级资源
    USER = DictItem(value="user", label="用户", sort=1)
    ROLE = DictItem(value="role", label="角色", sort=2)
    PERMISSION = DictItem(value="permission", label="权限", sort=3)
    TENANT = DictItem(value="tenant", label="租户", sort=4)
    
    # 租户级资源
    GOODS = DictItem(value="goods", label="商品", sort=10)
    ORDER = DictItem(value="order", label="订单", sort=11)
    INVENTORY = DictItem(value="inventory", label="库存", sort=12)


# ========== 操作类型 ==========
class ActionConst:
    """操作类型"""
    CREATE = DictItem(value="create", label="创建", sort=1)
    READ = DictItem(value="read", label="读取", sort=2)
    UPDATE = DictItem(value="update", label="更新", sort=3)
    DELETE = DictItem(value="delete", label="删除", sort=4)
    LIST = DictItem(value="list", label="列表", sort=5)





# ========== 账号绑定状态 ==========
class AccountBindStatusConst:
    """账号绑定状态"""
    PENDING = DictItem(value="pending", label="待验证", sort=1)
    VERIFIED = DictItem(value="verified", label="已验证", sort=2)
    DISABLED = DictItem(value="disabled", label="已禁用", sort=3)


# ========== 业务场景 ==========
class SceneConst:
    """业务场景"""
    ADMIN = DictItem(value="admin", label="管理后台", sort=1)
    APP = DictItem(value="app", label="移动端", sort=2)
    MERCHANT = DictItem(value="merchant", label="商户端", sort=3)


# ========== 角色编码 ==========
class RoleCodeConst:
    """角色编码 - 用于数据库存储和权限校验"""
    # 平台角色
    PLATFORM_SUPER_ADMIN = DictItem(value="platform_super_admin", label="平台超级管理员", sort=1)
    PLATFORM_ADMIN = DictItem(value="platform_admin", label="平台管理员", sort=2)
    PLATFORM_OPERATOR = DictItem(value="platform_operator", label="平台运营", sort=3)
    PLATFORM_AUDITOR = DictItem(value="platform_auditor", label="平台审计", sort=4)
    PLATFORM_NORMAL_USER = DictItem(value="platform_normal_user", label="平台普通用户", sort=5)

    # 租户角色
    TENANT_OWNER = DictItem(value="tenant_owner", label="租户所有者", sort=1)
    TENANT_ADMIN = DictItem(value="tenant_admin", label="租户管理员", sort=2)
    TENANT_MEMBER = DictItem(value="tenant_member", label="普通成员", sort=3)


# ========== 成员入驻类型 ==========
class MemberJoinTypeConst:
    """成员入驻类型"""
    PRIVATE = DictItem(value="private", label="定向邀请", sort=1)
    PUBLIC = DictItem(value="public", label="公开链接加入", sort=2)
    APPLY = DictItem(value="apply", label="用户自助申请", sort=3)


# ========== 审核状态 ==========
class AuditStatusConst:
    """审核状态"""
    PENDING = DictItem(value=0, label="待审核", sort=1)
    APPROVED = DictItem(value=1, label="已通过", sort=2)
    REJECTED = DictItem(value=2, label="已拒绝", sort=3)


# ========== 房屋状态 ==========
class HouseStatusConst:
    """房屋状态"""
    NORMAL = DictItem(value="normal", label="正常", sort=1)
    DAMAGED = DictItem(value="damaged", label="损坏", sort=2)
    DANGEROUS = DictItem(value="dangerous", label="危险", sort=3)


# ========== 鉴定相关 ==========
class IdentificationTypeConst:
    """鉴定类型"""
    INITIAL = DictItem(value="initial", label="初始鉴定", sort=1)
    ROUTINE = DictItem(value="routine", label="常规鉴定", sort=2)
    SPECIAL = DictItem(value="special", label="专项鉴定", sort=3)


class IdentificationStatusConst:
    """鉴定状态"""
    PENDING = DictItem(value="pending", label="待鉴定", sort=1)
    IN_PROGRESS = DictItem(value="in_progress", label="鉴定中", sort=2)
    COMPLETED = DictItem(value="completed", label="已完成", sort=3)


# ========== 分页参数 ==========
@dataclass(frozen=True)
class PaginationConst:
    """分页参数 - 可存数据库供管理员配置"""
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


# ========== 文件配置 ==========
@dataclass(frozen=True)
class FileExtensionConst:
    """文件扩展名 - 可存数据库"""
    IMAGE = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}
    DOC = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"}
    VIDEO = {"mp4", "avi", "mov", "wmv", "flv"}


@dataclass(frozen=True)
class FileSizeConst:
    """文件大小限制（字节）- 可存数据库"""
    MAX_IMAGE = 10 * 1024 * 1024    # 10MB
    MAX_DOC = 50 * 1024 * 1024      # 50MB
    MAX_VIDEO = 500 * 1024 * 1024   # 500MB


# ========== 存储路径 ==========
@dataclass(frozen=True)
class StoragePathConst:
    """存储路径 - 可存数据库"""
    AVATAR = "avatars"
    HOUSE = "houses"
    REPORT = "reports"
    TEMP = "temp"


# #############################################################################
# 第二部分：技术常量（仅后端使用的固定值，不支持配置覆盖）
# #############################################################################

# ========== 环境常量 ==========
@dataclass(frozen=True)
class EnvConst:
    """环境标识"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


# ========== 编码常量 ==========
@dataclass(frozen=True)
class EncodingConst:
    """编码常量"""
    UTF8 = "utf-8"
    GBK = "gbk"


# ========== 时间格式 ==========
@dataclass(frozen=True)
class DateTimeConst:
    """日期时间格式"""
    FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"


# ========== 时区和基础常量 ==========
@dataclass(frozen=True)
class BaseConst:
    """基础常量"""
    DEFAULT_TIMEZONE = "Asia/Shanghai"
    EMPTY_VALUES = (None, "", [], {}, set())


# ========== 正则表达式 ==========
@dataclass(frozen=True)
class RegexConst:
    """正则表达式"""
    PHONE = r"^1[3-9]\d{9}$"
    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    ID_CARD = r"^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$"
    PASSWORD_STRONG = r"^(?=.*[a-zA-Z])(?=.*\d).{6,}$|^(?=.*[a-z])(?=.*[A-Z]).{6,}$"
    USERNAME = r"^[a-zA-Z0-9._]{4,20}$"
    HOUSE_CODE = r"^HJ\d{8}$"
