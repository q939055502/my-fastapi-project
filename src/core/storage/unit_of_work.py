"""统一事务和工作单元管理器

确保数据库操作和Redis缓存操作的数据一致性，所有对数据库和Redis的操作都应该通过这个模块进行。"""
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from .database import SessionLocal
from .redis import cache_manager


class UnitOfWork:
    """工作单元模式实现

    统一管理数据库会话和Redis缓存操作，确保数据一致性。

    使用方式：
        with UnitOfWork() as uow:
            user = user_repository.get(uow.session, id=1)
            user.name = "new name"
            uow.commit()

        # 或者使用with_payload
        with UnitOfWork() as uow:
            result = uow.execute(
                action=lambda: user_repository.create(data, session=uow.session),
                cache_clear_patterns=["user:1:*"]
            )
    """

    def __init__(self):
        self.session: Session | None = None
        self._committed = False
        self._cache_clears: list[tuple[str, ...]] = []

    def __enter__(self):
        """进入上下文管理器，创建数据库会话"""
        self.session = SessionLocal()
        self._transaction = self.session.begin()
        self._committed = False
        self._cache_clears = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if exc_type:
            if self.session:
                self.session.rollback()
            self._clear_cache()
            return False

        if not self._committed and self.session:
            self.session.commit()

        self._clear_cache()

        if self.session:
            self.session.close()

        return True

    def commit(self):
        """提交事务"""
        if self.session:
            self.session.commit()
            self._committed = True

    def rollback(self):
        """回滚事务"""
        if self.session:
            self.session.rollback()
            self._committed = True

    def register_cache_clear(self, *patterns: str):
        """注册缓存清除模式"""
        self._cache_clears.append(patterns)

    def _clear_cache(self):
        """清除所有注册的缓存"""
        for patterns in self._cache_clears:
            for pattern in patterns:
                cleared = cache_manager.clear_pattern(pattern)
                if cleared > 0:
                    from src.core.log import logger
                    logger.debug(f"缓存已清除: {pattern}, 数量: {cleared}")

    @contextmanager
    def transaction(self):
        """嵌套事务上下文管理器"""
        nested_transaction = self.session.begin_nested()
        try:
            yield nested_transaction
        except Exception:
            nested_transaction.rollback()
            raise

    def execute(
        self,
        action: Callable[[Session], Any],
        cache_clear_patterns: list[str] | None = None,
        cache_key: str | None = None,
        cache_value: Any | None = None,
        cache_ttl: int | None = None
    ) -> Any:
        """执行数据库操作并管理缓存

        Args:
            action: 数据库操作函数，接受session参数
            cache_clear_patterns: 操作成功后要清除的缓存模式列表
            cache_key: 要设置的缓存键
            cache_value: 要设置的缓存值
            cache_ttl: 缓存过期时间（秒）

        Returns:
            数据库操作的结果
        """
        result = action(self.session)

        self._committed = True
        self.session.commit()

        if cache_clear_patterns:
            self.register_cache_clear(*cache_clear_patterns)
            self._clear_cache()

        if cache_key and cache_value is not None:
            cache_manager.set(cache_key, cache_value, cache_ttl)

        return result


def get_unit_of_work() -> UnitOfWork:
    """获取UnitOfWork实例（依赖注入函数）"""
    return UnitOfWork()
