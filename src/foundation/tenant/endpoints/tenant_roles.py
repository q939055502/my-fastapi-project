"""
租户角色管理接口

管理租户级角色(tenant_id为具体租户ID),仅该租户内生效
"""
from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.core.base.schema_base import PaginationResponse
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, swagger_responses
from src.core.storage import TransactionManager
from src.core.storage.uuid_resolver import uuid_resolver
from src.foundation.iam.rbac.schemas.role import RoleCreate, RoleUpdate
from src.foundation.iam.rbac.service.role_service import role_service

router = APIRouter(
    tags=["租户管理-角色"],
)


def _get_tenant_id_by_uuid(tenant_uuid: UUID, session) -> int:
    """通过租户UUID获取租户ID"""
    tenant_id = uuid_resolver.resolve(session, "tenant", str(tenant_uuid))
    if not tenant_id:
        from src.core.exceptions import BusinessException
        raise BusinessException(40401, detail="租户不存在")
    return tenant_id


@router.post(
    "/",
    summary="创建租户角色",
)
@apply_rate_limit("30/minute")
def create_tenant_role(request: Request, tenant_uuid: UUID, role_in: RoleCreate) -> ApiResponse[dict]:
    """
    创建租户角色

    【类型】管理接口(需登录)
    【权限】租户管理员
    【功能】在租户内创建角色,仅该租户生效
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.create_tenant_role(tenant_id, role_in)
    return ApiResponse(code=20000, data=data, msg="租户角色创建成功")


@router.put(
    "/{role_uuid}",
    summary="更新租户角色",
    responses=swagger_responses(
        codes=[40401, 40000, 40300],
        success_msg="租户角色不存在或租户不存在",
    ),
)
@apply_rate_limit("30/minute")
def update_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID, role_in: RoleUpdate) -> ApiResponse[dict]:
    """
    更新租户角色

    【类型】管理接口(需登录)
    【权限】租户管理员
    【功能】更新租户内角色信息
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.update_tenant_role(tenant_id, role_uuid, role_in)
    return ApiResponse(code=20000, data=data, msg="租户角色更新成功")


@router.put(
    "/{role_uuid}/permissions",
    summary="更新租户角色权限",
    responses=swagger_responses(
        codes=[40401, 40300],
        success_msg="租户角色不存在或租户不存在",
    ),
)
@apply_rate_limit("30/minute")
def update_tenant_role_permissions(request: Request, tenant_uuid: UUID, role_uuid: UUID, role_in: RoleUpdate) -> ApiResponse[None]:
    """
    更新租户角色权限

    【类型】管理接口(需登录�?    【权限】租户管理员
    【功能】更新租户角色的权限列表
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    role_service.update_tenant_role_permissions(tenant_id, role_uuid, role_in.permission_uuids or [])
    return ApiResponse(code=20000, msg="权限更新成功")


@router.get("/list", summary="获取租户角色列表")
@apply_rate_limit("60/minute")
def list_tenant_roles(
    request: Request,
    tenant_uuid: UUID,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="角色名称,用于查询"),
) -> ApiResponse[PaginationResponse[dict]]:
    """
    获取租户角色列表

    【类型】管理接口(需登录)
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
    return ApiResponse(
        code=20000,
        data=PaginationResponse(
            list=data,
            pagination={"total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0}
        ),
        msg="操作成功"
    )


@router.get(
    "/{role_uuid}",
    summary="获取租户角色详情",
)
@apply_rate_limit("60/minute")
def get_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID) -> ApiResponse[dict]:
    """
    获取租户角色详情

    【类型】管理接口(需登录)
    【权限】租户管理员
    【功能】获取单个租户角色的详细信息
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.get_tenant_role_detail(tenant_id, role_uuid)
    return ApiResponse(code=20000, data=data)


@router.get(
    "/{role_uuid}/permissions",
    summary="获取租户角色权限",
    responses=swagger_responses(
        codes=[40401],
        success_msg="租户角色不存在或租户不存在",
    ),
)
@apply_rate_limit("60/minute")
def get_tenant_role_permissions(request: Request, tenant_uuid: UUID, role_uuid: UUID) -> ApiResponse[list]:
    """
    获取租户角色权限

    【类型】管理接口(需登录)
    【权限】租户管理员
    【功能】获取租户角色的权限列表
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    data = role_service.get_tenant_role_detail(tenant_id, role_uuid)
    return ApiResponse(code=20000, data=data.get("permissions", []))


@router.delete(
    "/{role_uuid}",
    summary="删除租户角色",
)
@apply_rate_limit("30/minute")
def delete_tenant_role(request: Request, tenant_uuid: UUID, role_uuid: UUID) -> ApiResponse[None]:
    """
    删除租户角色

    【类型】管理接口(需登录)
    【权限】租户管理员
    【功能】删除租户内角色(软删除)
    """
    with TransactionManager() as tm:
        tenant_id = _get_tenant_id_by_uuid(tenant_uuid, tm.session)
    role_service.delete_tenant_role(tenant_id, role_uuid)
    return ApiResponse(code=20000, msg="租户角色删除成功")
