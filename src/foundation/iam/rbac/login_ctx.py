"""
用户登录上下文缓存模块

Context 设计理念:
  - 用 dataclass 定义明确的字段结构
  - 提供 get() / invalidate() 方法
  - Redis 存 dict, get() 时转成 dataclass 对象返回给业务代码
  - 业务代码用对象属性访问: ctx.platform.role_ids

缓存 key: login_ctx:{user_id}
subject_type: 0=平台用户, subject_id=user_id; 1=租户成员, subject_id=member.subject_id

缓存失效:
  RoleSubject 绑/解绑 → invalidate_login_ctx()
  RolePermission 增/删 → invalidate_login_ctx()
  DataScopeRule 增/删改 → invalidate_login_ctx()
  OrgSubject 绑/解绑   → invalidate_login_ctx()
  Member 归属变更      → invalidate_login_ctx()
"""

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select

from src.core.constants import RoleCodeConst
from src.core.storage import TransactionManager, cache_manager
from src.models.platform import (
    DataScopeRule,
    Permission,
    Role,
    RolePermission,
    RoleSubject,
    User,
)
from src.models.platform.system import OrgSubject
from src.models.tenant.core import Member


LOGIN_CTX_RESOURCE = "login_ctx"

_PLATFORM_SUBJECT_TYPE = 0
_TENANT_SUBJECT_TYPE = 1


@dataclass
class UserInfo:
    id: int
    username: str
    alias: str
    avatar: str | None = None
    is_active: bool = True


@dataclass
class MemberInfo:
    id: int
    user_id: int
    tenant_id: int
    subject_id: int
    is_owner: bool = False


@dataclass
class DataScopeRuleItem:
    role_id: int
    permission_id: int
    dimension_type: str
    match_type: str
    dimension_value: str


@dataclass
class SubjectBlock:
    """单个主体(平台或租户)的角色 + 权限 + 数据范围 + 组织归属"""
    role_ids: list[int] = field(default_factory=list)
    permission_codes: list[str] = field(default_factory=list)
    data_scope_rules: list[DataScopeRuleItem] = field(default_factory=list)
    org_ids: list[int] = field(default_factory=list)
    is_super_admin: bool = False
    member_info: MemberInfo | None = None


@dataclass
class LoginContext:
    """用户登录上下文

    用法:
        ctx = get_login_ctx(user_id=1, member_id=100)
        if ctx.is_super_admin:
            ...
        ctx.platform.role_ids              # 平台角色列表
        ctx.platform.permission_codes      # 平台权限码列表
        ctx.platform.data_scope_rules      # 平台数据范围规则
        ctx.platform.org_ids               # 平台归属组织节点
        ctx.tenant.role_ids                # 租户角色列表 (tenant 可能为 None)
        ctx.tenant.member_info             # 租户成员基本信息
        ctx.user_info.username             # 用户基本信息
    """
    user_info: UserInfo
    platform: SubjectBlock
    tenant: SubjectBlock | None = None
    is_super_admin: bool = False


# ---------- 序列化 ----------

def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "alias": getattr(user, "alias", user.username),
        "avatar": getattr(user, "avatar", None),
        "is_active": getattr(user, "is_active", True),
    }


def _member_to_dict(member: Member) -> dict:
    return {
        "id": member.id,
        "user_id": member.user_id,
        "tenant_id": member.tenant_id,
        "subject_id": member.subject_id,
        "is_owner": member.is_owner,
    }


def _scope_rule_to_dict(rule: DataScopeRule) -> dict:
    return {
        "role_id": rule.role_id,
        "permission_id": rule.permission_id,
        "dimension_type": rule.dimension_type,
        "match_type": rule.match_type,
        "dimension_value": rule.dimension_value,
    }


def _dict_to_user_info(data: dict) -> UserInfo:
    return UserInfo(**data)


def _dict_to_member_info(data: dict) -> MemberInfo:
    return MemberInfo(**data)


def _dict_to_subject_block(data: dict) -> SubjectBlock:
    rules = [DataScopeRuleItem(**r) for r in data.get("data_scope_rules", [])]
    member_info: MemberInfo | None = None
    if data.get("member_info"):
        member_info = _dict_to_member_info(data["member_info"])
    return SubjectBlock(
        role_ids=data.get("role_ids", []),
        permission_codes=data.get("permission_codes", []),
        data_scope_rules=rules,
        org_ids=data.get("org_ids", []),
        is_super_admin=data.get("is_super_admin", False),
        member_info=member_info,
    )


def _dict_to_login_ctx(data: dict) -> LoginContext:
    platform_block = _dict_to_subject_block(data["platform"])
    tenant_block = None
    if data.get("tenant"):
        tenant_block = _dict_to_subject_block(data["tenant"])
    return LoginContext(
        user_info=_dict_to_user_info(data["user_info"]),
        platform=platform_block,
        tenant=tenant_block,
        is_super_admin=data["is_super_admin"],
    )


# ---------- 查库 ----------

def _load_subject_block(subject_type: int, subject_id: int, session) -> dict:
    """加载单个主体的 role_ids + permission_codes + data_scope_rules + org_ids (dict)"""
    role_ids = [
        row[0] for row in session.execute(
            select(RoleSubject.role_id).where(
                RoleSubject.subject_type == subject_type,
                RoleSubject.subject_id == subject_id,
            )
        )
    ]

    if not role_ids:
        return {
            "role_ids": [],
            "permission_codes": [],
            "data_scope_rules": [],
            "org_ids": [],
            "is_super_admin": False,
        }

    role_codes = {
        row[0]: row[1]
        for row in session.execute(
            select(Role.id, Role.code).where(Role.id.in_(role_ids))
        )
    }

    is_super_admin = any(
        code == RoleCodeConst.PLATFORM_SUPER_ADMIN.value
        for code in role_codes.values()
    )

    perm_ids = [
        row[0] for row in session.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id.in_(role_ids))
        )
    ]

    if perm_ids:
        permission_codes = [
            row[0] for row in session.execute(
                select(Permission.permission_code).where(Permission.id.in_(perm_ids))
            )
        ]
    else:
        permission_codes = []

    scope_rules_orm = list(session.execute(
        select(DataScopeRule).where(
            DataScopeRule.role_id.in_(role_ids),
        )
    ).scalars().all())

    org_ids = [
        row[0] for row in session.execute(
            select(OrgSubject.org_id).where(
                OrgSubject.subject_type == subject_type,
                OrgSubject.subject_id == subject_id,
            )
        )
    ]

    return {
        "role_ids": role_ids,
        "permission_codes": permission_codes,
        "data_scope_rules": [_scope_rule_to_dict(r) for r in scope_rules_orm],
        "org_ids": org_ids,
        "is_super_admin": is_super_admin,
    }


def _build_login_ctx_dict(user_id: int, member_id: int | None) -> dict:
    """一次性查出 User + 平台身份 + 租户身份 → 组装 dict"""
    with TransactionManager() as tm:
        user = tm.session.execute(
            select(User).where(User.id == user_id)
        ).scalars().first()

        user_info = _user_to_dict(user) if user else None

        platform_dict = _load_subject_block(_PLATFORM_SUBJECT_TYPE, user_id, tm.session)

        tenant_dict: dict[str, Any] | None = None
        tenant_super_admin = False

        if member_id:
            member = tm.session.execute(
                select(Member).where(Member.subject_id == member_id)
            ).scalars().first()

            if member:
                member_info = _member_to_dict(member)
                tenant_subject_id = member.subject_id

                tenant_inner = _load_subject_block(
                    _TENANT_SUBJECT_TYPE, tenant_subject_id, tm.session)

                tenant_dict = {
                    "member_info": member_info,
                    **tenant_inner,
                }
                tenant_super_admin = tenant_inner["is_super_admin"]

        is_super_admin = platform_dict["is_super_admin"] or tenant_super_admin

    return {
        "user_info": user_info,
        "platform": platform_dict,
        "tenant": tenant_dict,
        "is_super_admin": is_super_admin,
    }


# ---------- 对外 API ----------

def get_login_ctx(user_id: int, member_id: int | None = None) -> LoginContext | None:
    """获取登录上下文(懒加载 + 缓存)

    先查 Redis 缓存 → 命中直接转成 LoginContext dataclass 返回
    未命中 → 一次性查库 → 写缓存 → 转 dataclass 返回

    Returns:
        LoginContext 对象, 或 None(用户不存在)
    """
    cache_key = str(user_id)

    cached = cache_manager.get_global(LOGIN_CTX_RESOURCE, cache_key)
    if cached is not None:
        if member_id is None and cached.get("tenant") is None:
            return _dict_to_login_ctx(cached)

        if member_id is not None:
            tenant_block = cached.get("tenant")
            if tenant_block and tenant_block.get("member_info", {}).get("subject_id") == member_id:
                return _dict_to_login_ctx(cached)

    ctx_dict = _build_login_ctx_dict(user_id, member_id)

    if ctx_dict["user_info"] is None:
        return None

    cache_manager.set_global(LOGIN_CTX_RESOURCE, cache_key, ctx_dict)

    return _dict_to_login_ctx(ctx_dict)


def invalidate_login_ctx(user_id: int | None = None) -> None:
    """清除登录上下文缓存

    Args:
        user_id: 指定用户ID, None 则全量清(角色权限变更等影响所有用户时)
    """
    if user_id is not None:
        cache_manager.delete_global(LOGIN_CTX_RESOURCE, str(user_id))
    else:
        cache_manager._clear_pattern_raw(f"{LOGIN_CTX_RESOURCE}:*")
