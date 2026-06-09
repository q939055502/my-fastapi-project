
"""
Redis令牌管理器

实现基于Redis的令牌存储方案，支持以下5种Key模式：
1. access:{access_token} - 访问令牌存储，Value为User ID
2. refresh:{refresh_token} - 刷新令牌存储，Value为JSON(user_id, linked_access)
3. user:tokens:{user_id} - 用户令牌集合，存储所有有效令牌
4. user:device:{user_id}:{device_id} - 设备信息（可选）
5. user:perm:{user_id} - 权限/角色缓存
"""

import json
import secrets

import redis
from src.common.core.config import settings
from src.common.core.log import logger


class TokenManager:
    """Redis令牌管理器"""

    PREFIX_ACCESS = "access"
    PREFIX_REFRESH = "refresh"
    PREFIX_USER_TOKENS = "user:tokens"
    PREFIX_USER_DEVICE = "user:device"
    PREFIX_USER_PERM = "user:perm"
    PREFIX_TEMP_LOGIN = "temp_login"

    TEMP_LOGIN_EXPIRE_SECONDS = 300  # 临时凭证有效期：5分钟

    def __init__(self):
        self.redis: redis.Redis | None = None

    def connect(self):
        """连接Redis"""
        if self.redis is None:
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True,
                )
                self.redis.ping()
                logger.info("TokenManager: Redis连接成功")
            except Exception as e:
                logger.warning(f"TokenManager: Redis连接失败: {str(e)}，令牌管理功能将被禁用")
                self.redis = None

    def disconnect(self):
        """断开Redis连接"""
        if self.redis:
            self.redis.close()
            self.redis = None
            logger.info("TokenManager: Redis连接已断开")

    def _is_available(self) -> bool:
        """检查Redis是否可用"""
        return self.redis is not None

    def _get_access_key(self, access_token: str) -> str:
        """获取访问令牌Key"""
        return f"{self.PREFIX_ACCESS}:{access_token}"

    def _get_refresh_key(self, refresh_token: str) -> str:
        """获取刷新令牌Key"""
        return f"{self.PREFIX_REFRESH}:{refresh_token}"

    def _get_user_tokens_key(self, user_id: int) -> str:
        """获取用户令牌集合Key"""
        return f"{self.PREFIX_USER_TOKENS}:{user_id}"

    def _get_user_perm_key(self, user_id: int) -> str:
        """获取用户权限缓存Key"""
        return f"{self.PREFIX_USER_PERM}:{user_id}"

    def store_access_token(
        self,
        access_token: str,
        user_id: int,
        ttl_seconds: int
    ) -> bool:
        """存储访问令牌"""
        if not self._is_available():
            logger.warning("TokenManager: Redis未连接，无法存储访问令牌")
            return False

        try:
            key = self._get_access_key(access_token)
            self.redis.setex(key, ttl_seconds, str(user_id))
            logger.debug(f"TokenManager: 存储访问令牌 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 存储访问令牌失败: {str(e)}")
            return False

    def store_refresh_token(
        self,
        refresh_token: str,
        user_id: int,
        linked_access_token: str,
        ttl_seconds: int
    ) -> bool:
        """存储刷新令牌"""
        if not self._is_available():
            logger.warning("TokenManager: Redis未连接，无法存储刷新令牌")
            return False

        try:
            key = self._get_refresh_key(refresh_token)
            value = json.dumps({
                "user_id": user_id,
                "linked_access": linked_access_token
            })
            self.redis.setex(key, ttl_seconds, value)
            logger.debug(f"TokenManager: 存储刷新令牌 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 存储刷新令牌失败: {str(e)}")
            return False

    def add_user_token(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str,
        ttl_seconds: int
    ) -> bool:
        """将令牌添加到用户令牌集合

        设计说明：
        - 只存储 refresh_token，因为通过 refresh_token 可以找到关联的 access_token
        - 撤销用户所有令牌时，通过 refresh_token 批量清理关联的 access_token
        """
        if not self._is_available():
            logger.warning("TokenManager: Redis未连接，无法添加用户令牌")
            return False

        try:
            key = self._get_user_tokens_key(user_id)
            self.redis.sadd(key, refresh_token)
            self.redis.expire(key, ttl_seconds)
            logger.debug(f"TokenManager: 添加用户令牌到集合 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 添加用户令牌失败: {str(e)}")
            return False

    def get_user_id_by_access_token(self, access_token: str) -> int | None:
        """通过访问令牌获取用户ID"""
        if not self._is_available():
            return None

        try:
            key = self._get_access_key(access_token)
            user_id = self.redis.get(key)
            if user_id:
                return int(user_id)
            return None
        except Exception as e:
            logger.error(f"TokenManager: 获取用户ID失败: {str(e)}")
            return None

    def get_refresh_token_data(
        self,
        refresh_token: str
    ) -> dict | None:
        """获取刷新令牌数据"""
        if not self._is_available():
            return None

        try:
            key = self._get_refresh_key(refresh_token)
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"TokenManager: 获取刷新令牌数据失败: {str(e)}")
            return None

    def validate_access_token(self, access_token: str) -> bool:
        """验证访问令牌是否有效"""
        if not self._is_available():
            return False

        try:
            key = self._get_access_key(access_token)
            exists = self.redis.exists(key) > 0
            return exists
        except Exception as e:
            logger.error(f"TokenManager: 验证访问令牌失败: {str(e)}")
            return False

    def revoke_access_token(self, access_token: str) -> bool:
        """撤销访问令牌"""
        if not self._is_available():
            return False

        try:
            key = self._get_access_key(access_token)
            result = self.redis.delete(key)
            logger.info(f"TokenManager: 撤销访问令牌 result={result}")
            return result > 0
        except Exception as e:
            logger.error(f"TokenManager: 撤销访问令牌失败: {str(e)}")
            return False

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """撤销刷新令牌"""
        if not self._is_available():
            return False

        try:
            key = self._get_refresh_key(refresh_token)
            result = self.redis.delete(key)
            logger.info(f"TokenManager: 撤销刷新令牌 result={result}")
            return result > 0
        except Exception as e:
            logger.error(f"TokenManager: 撤销刷新令牌失败: {str(e)}")
            return False

    def revoke_user_all_tokens(self, user_id: int) -> int:
        """撤销用户所有令牌（踢人下线）"""
        if not self._is_available():
            return 0

        try:
            user_tokens_key = self._get_user_tokens_key(user_id)
            refresh_tokens = self.redis.smembers(user_tokens_key)

            if not refresh_tokens:
                return 0

            count = 0
            for refresh_token in refresh_tokens:
                refresh_key = self._get_refresh_key(refresh_token)
                refresh_data = self.redis.get(refresh_key)

                if refresh_data:
                    data = json.loads(refresh_data)
                    linked_access = data.get("linked_access")
                    if linked_access:
                        access_key = self._get_access_key(linked_access)
                        if self.redis.exists(access_key):
                            self.redis.delete(access_key)
                            count += 1

                if self.redis.exists(refresh_key):
                    self.redis.delete(refresh_key)
                    count += 1

            self.redis.delete(user_tokens_key)

            logger.info(f"TokenManager: 撤销用户所有令牌 user_id={user_id} count={count}")
            return count
        except Exception as e:
            logger.error(f"TokenManager: 撤销用户所有令牌失败: {str(e)}")
            return 0

    def revoke_token_pair(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int
    ) -> bool:
        """撤销令牌对"""
        if not self._is_available():
            return False

        try:
            access_key = self._get_access_key(access_token)
            refresh_key = self._get_refresh_key(refresh_token)
            user_tokens_key = self._get_user_tokens_key(user_id)

            self.redis.delete(access_key, refresh_key)
            self.redis.srem(user_tokens_key, access_token, refresh_token)

            logger.info(f"TokenManager: 撤销令牌对 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 撤销令牌对失败: {str(e)}")
            return False

    def remove_token_from_user_set(
        self,
        user_id: int,
        access_token: str,
        refresh_token: str
    ) -> bool:
        """从用户令牌集合中移除令牌"""
        if not self._is_available():
            return False

        try:
            user_tokens_key = self._get_user_tokens_key(user_id)
            self.redis.srem(user_tokens_key, refresh_token)
            logger.debug(f"TokenManager: 从用户集合移除令牌 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 从用户集合移除令牌失败: {str(e)}")
            return False

    def store_user_permissions(
        self,
        user_id: int,
        permissions: dict,
        ttl_seconds: int = 3600
    ) -> bool:
        """存储用户权限缓存"""
        if not self._is_available():
            return False

        try:
            key = self._get_user_perm_key(user_id)
            value = json.dumps(permissions, ensure_ascii=False, default=str)
            self.redis.setex(key, ttl_seconds, value)
            logger.debug(f"TokenManager: 存储用户权限 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 存储用户权限失败: {str(e)}")
            return False

    def get_user_permissions(self, user_id: int) -> dict | None:
        """获取用户权限缓存"""
        if not self._is_available():
            return None

        try:
            key = self._get_user_perm_key(user_id)
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"TokenManager: 获取用户权限失败: {str(e)}")
            return None

    def clear_user_permissions(self, user_id: int) -> bool:
        """清除用户权限缓存"""
        if not self._is_available():
            return False

        try:
            key = self._get_user_perm_key(user_id)
            self.redis.delete(key)
            logger.debug(f"TokenManager: 清除用户权限 user_id={user_id}")
            return True
        except Exception as e:
            logger.error(f"TokenManager: 清除用户权限失败: {str(e)}")
            return False

    def _get_temp_login_key(self, temp_token: str) -> str:
        """获取临时登录凭证Key"""
        return f"{self.PREFIX_TEMP_LOGIN}:{temp_token}"

    def store_temp_login_token(
        self,
        user_id: int,
        username: str,
        tenant_memberships: list[dict],
        users: list[dict] = None
    ) -> str:
        """存储临时登录凭证，返回临时token"""
        if not self._is_available():
            logger.warning("TokenManager: Redis未连接，无法存储临时凭证")
            return ""

        try:
            # 生成强随机临时token
            temp_token = secrets.token_urlsafe(32)
            key = self._get_temp_login_key(temp_token)

            value = json.dumps({
                "user_id": user_id,
                "username": username,
                "users": users or [],
                "tenant_memberships": tenant_memberships
            })

            self.redis.setex(key, self.TEMP_LOGIN_EXPIRE_SECONDS, value)
            logger.debug(f"TokenManager: 存储临时登录凭证 user_id={user_id}")
            return temp_token
        except Exception as e:
            logger.error(f"TokenManager: 存储临时凭证失败: {str(e)}")
            return ""

    def get_temp_login_token(self, temp_token: str) -> dict | None:
        """获取临时登录凭证数据"""
        if not self._is_available():
            return None

        try:
            key = self._get_temp_login_key(temp_token)
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"TokenManager: 获取临时凭证失败: {str(e)}")
            return None

    def revoke_temp_login_token(self, temp_token: str) -> bool:
        """撤销临时登录凭证（单次使用后删除）"""
        if not self._is_available():
            return False

        try:
            key = self._get_temp_login_key(temp_token)
            result = self.redis.delete(key)
            logger.debug(f"TokenManager: 撤销临时登录凭证 result={result}")
            return result > 0
        except Exception as e:
            logger.error(f"TokenManager: 撤销临时凭证失败: {str(e)}")
            return False


token_manager = TokenManager()
