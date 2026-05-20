"""
认证接口（登录、Token刷新）
"""

from fastapi import APIRouter, Request, HTTPException

from src.models.sys.user import User
from src.repositories.sys.user_repository import user_repository
from src.core.response import success
from src.schemas.sys.login import CredentialsSchema, JWTOut, RefreshTokenRequest, TokenRefreshOut
from src.core.config import settings
from src.core.security import create_token_pair, verify_token
from src.core.storage import UnitOfWork, token_manager
from src.core.log import logger
from src.core.rate_limit import apply_rate_limit


router = APIRouter()


@router.post("/login", summary="用户登录")
@apply_rate_limit()
def login_access_token(request: Request, credentials: CredentialsSchema):
    """
    用户登录接口

    【类型】公开接口（无需登录）
    【权限】无需认证
    【限流】5次/分钟（防暴力破解）
    【功能】验证用户名密码，返回 access_token 和 refresh_token
    """
    with UnitOfWork() as uow:
        user: User = user_repository.authenticate(credentials, session=uow.session)
        user_repository.update_last_login(user.id, session=uow.session)
        uow.commit()

    access_token, refresh_token = create_token_pair(
        user_id=user.id, username=user.username
    )

    access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    token_manager.store_access_token(access_token, user.id, access_ttl)
    token_manager.store_refresh_token(refresh_token, user.id, access_token, refresh_ttl)
    token_manager.add_user_token(user.id, access_token, refresh_token, refresh_ttl)

    data = JWTOut(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        expires_in=access_ttl,
    )
    return success(data=data.model_dump())


@router.post("/refresh", summary="刷新token")
@apply_rate_limit("10/minute")
def refresh_access_token(request: Request, refresh_request: RefreshTokenRequest):
    """
    刷新访问令牌

    【类型】认证接口
    【权限】使用 refresh_token 换发新token（无需 access_token）
    【限流】10次/分钟
    【功能】用 refresh_token 获取新的 access_token 和 refresh_token
    """
    refresh_data = token_manager.get_refresh_token_data(refresh_request.refresh_token)
    if not refresh_data:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    payload = verify_token(refresh_request.refresh_token, token_type="refresh")

    with UnitOfWork() as uow:
        user = user_repository.get(id=payload["user_id"], session=uow.session)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户不存在或已被禁用")

    old_access_token = refresh_data.get("linked_access")

    if old_access_token:
        token_manager.revoke_access_token(old_access_token)
    token_manager.revoke_refresh_token(refresh_request.refresh_token)

    access_token, new_refresh_token = create_token_pair(
        user_id=user.id, username=user.username
    )

    access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    token_manager.store_access_token(access_token, user.id, access_ttl)
    token_manager.store_refresh_token(new_refresh_token, user.id, access_token, refresh_ttl)
    token_manager.add_user_token(user.id, access_token, new_refresh_token, refresh_ttl)

    data = TokenRefreshOut(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=access_ttl,
    )

    return success(data=data.model_dump())