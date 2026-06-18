"""
租户角色管理接口

管理租户级角色（tenant_id为具体租户ID），仅该租户内生效。
"""
from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success, success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam.rbac.schemas.role import RoleCreate, RoleUpdate
from src.foundation.iam.rbac.service.role_service import role_service
from src.foundation.tenant.repository.tenant_repository import tenant_repository
from src.core.storage import TransactionManager

router = APIRouter(
    tags=["租户管理-角色"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


def _get_tenant_id_by_uuid(tenant_uuid: UUID, session) -> int:
    """通过租户UUID获取租户ID"""
    tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=session)
    if not tenant:
        from src.core.exceptions import BusinessException
        raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")
    return tenant.id


@router.post(
    "/",
    summary="创建租户角色",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="角色名称或编码已存在"
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="禁止创建系统内置角色"
        ),
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_tenant_role(request: Request, tenant_uuid: UUID, role_in: RoleCreate):
    """
    创建租户角色

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】在租户内创建角色，仅该租户生效
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.create_tenant_role(tenant_id, role_in)
    return success(data=data, msg="租户角色创建成功")


@router.put(
    "/{role_uuid}",
    summary="更新租户角色",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户角色不存在或租户不存在"
        ),
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="角色名称或编码已存在"
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="系统内置角色不可修改"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID, role_in: RoleUpdate):
    """
    更新租户角色

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】更新租户内角色信息
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.update_tenant_role(tenant_id, role_uuid, role_in)
    return success(data=data, msg="租户角色更新成功")


@router.put(
    "/{role_uuid}/permissions",
    summary="更新租户角色权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户角色不存在或租户不存在"
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="系统内置角色不可修改权限"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_tenant_role_permissions(request: Request, tenant_uuid: UUID, role_uuid: UUID, role_in: RoleUpdate):
    """
    更新租户角色权限

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】更新租户角色的权限列表
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    role_service.update_tenant_role_permissions(tenant_id, role_uuid, role_in.permission_uuids or [])
    return success(msg="权限更新成功")


@router.get("/list", summary="获取租户角色列表")
@apply_rate_limit("60/minute")
def list_tenant_roles(
    request: Request,
    tenant_uuid: UUID,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="角色名称，用于查询"),
):
    """
    获取租户角色列表

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】分页查询租户内角色
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    total, data = role_service.get_tenant_role_list(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        name=name
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{role_uuid}",
    summary="获取租户角色详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户角色不存在或租户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID):
    """
    获取租户角色详情

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】获取单个租户角色的详细信息
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.get_tenant_role_detail(tenant_id, role_uuid)
    return success(data=data)


@router.get(
    "/{role_uuid}/permissions",
    summary="获取租户角色权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户角色不存在或租户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_tenant_role_permissions(request: Request, tenant_uuid: UUID, role_uuid: UUID):
    """
    获取租户角色权限

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】获取租户角色的权限列表
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.get_tenant_role_detail(tenant_id, role_uuid)
    return success(data=data.get("permissions", []))


@router.delete(
    "/{role_uuid}",
    summary="删除租户角色",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="租户角色不存在或租户不存在"
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="系统内置角色不可删除"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID):
    """
    删除租户角色

    【类型】管理接口（需登录）
    【权限】租户管理员
    【功能】删除租户内角色（软删除）
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    role_service.delete_tenant_role(tenant_id, role_uuid)
    return success(msg="租户角色删除成功")