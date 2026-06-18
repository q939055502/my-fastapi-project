def _build_login_result(self, user: User, access_token: str, refresh_token: str, access_ttl: int) -> dict[str, Any]:
    """组装登录成功返回结果"""
    # 获取用户角色和权限
    with TransactionManager() as tm:
        roles = role_repository.get_user_roles(user.id, session=tm.session)
        permissions = role_repository.get_user_permissions(user.id, session=tm.session)
    
    # 获取用户基本信息（排除敏感字段）
    user_info = {
        "uuid": str(user.uuid),
        "username": user.username,
        "email": user.email,
        "alias": user.alias,
        "avatar": user.avatar,
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": access_ttl,
        "user": user_info,
        "roles": [r.code for r in roles],
        "permissions": [p.permission_code for p in permissions],
    }


def _store_tokens(self, user_id: int, access_token: str, refresh_token: str, access_ttl: int, refresh_ttl: int) -> None:
    """存储令牌到Redis"""
    token_manager.store_access_token(access_token, user_id, access_ttl)
    token_manager.store_refresh_token(refresh_token, user_id, access_token, refresh_ttl)
    token_manager.add_user_token(user_id, access_token, refresh_token, refresh_ttl)

