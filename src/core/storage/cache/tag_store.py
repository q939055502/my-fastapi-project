"""标签版本存储（控制平面）

管理标签的版本元数据，独立于业务缓存数据。
- 权威源: Redis (cache_tag:version:{tag})
- 本地缓存: 2 秒 TTL，减少 Redis 查询
- 失效方式: INCR 原子递增，旧键自然过期
"""

import hashlib
import time

from . import dogpile_config as _dc

TAG_VERSION_PREFIX = "cache_tag:version:"
_LOCAL_CACHE_TTL = 2  # 秒


class TagStore:
    """标签版本存储

    内部分层:
    - 控制平面: 标签版本元数据（本类管理）
    - 数据平面: 业务缓存数据（dogpile.cache 管理，不在本类范围）

    标签版本存储在 Redis 中，每个标签一个独立 String 键:
        cache_tag:version:role:all      → 3
        cache_tag:version:role:1        → 5
        cache_tag:version:tenant:1001   → 2
    """

    def __init__(self):
        self._local_cache: dict[str, tuple[int, float]] = {}

    def get_tag_version(self, tag: str) -> int:
        """获取标签版本号

        先查本地缓存（2 秒 TTL），未命中再查 Redis 权威值。
        Redis 不可用时返回 0，缓存仅靠 TTL 失效。
        """
        now = time.time()

        # 查本地缓存
        if tag in self._local_cache:
            version, expire_at = self._local_cache[tag]
            if now < expire_at:
                return version

        # 查 Redis 权威值
        if _dc.is_l2_available():
            key = f"{TAG_VERSION_PREFIX}{tag}"
            version = _dc.l2_get_int(key)
        else:
            version = 0

        self._local_cache[tag] = (version, now + _LOCAL_CACHE_TTL)
        return version

    def increment_tag(self, tag: str) -> int:
        """原子递增标签版本

        使用 Redis INCR 原子操作，递增后清除本地缓存。
        Redis 不可用时返回 0（无操作）。
        """
        # 清除本地缓存，下次读取强制拉最新值
        self._local_cache.pop(tag, None)

        if _dc.is_l2_available():
            key = f"{TAG_VERSION_PREFIX}{tag}"
            return _dc.l2_incr(key)
        return 0

    def calc_tag_hash(self, tags: list[str] | None) -> str:
        """根据标签列表计算版本哈希

        将所有标签+版本号按字典序拼接，取 md5 前 16 位 hex。
        - 无标签时返回 "v0"（静态哈希，仅靠 TTL 失效）
        - 任一标签版本变化，哈希结果完全不同
        """
        if not tags:
            return "v0"

        sorted_tags = sorted(tags)
        version_parts = [f"{t}={self.get_tag_version(t)}" for t in sorted_tags]
        version_str = "|".join(version_parts)
        return hashlib.md5(version_str.encode("utf-8")).hexdigest()[:16]

    def invalidate(self, tags: list[str]) -> None:
        """递增一组标签的版本号

        用于缓存失效：递增标签版本后，所有携带该标签的缓存键
        因 tag_hash 变化而无人访问，旧键依靠 TTL 自然淘汰。
        """
        for tag in tags:
            self.increment_tag(tag)


tag_store = TagStore()
