"""事务管理器（Transaction Manager）

提供简洁的事务管理能力，确保数据库操作的原子性。
"""

from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from .database import SessionLocal


class TransactionManager:
    """事务管理器

    统一管理数据库会话和事务操作，确保数据一致性。

    使用方式：
        with TransactionManager() as tm:
            user = user_repository.get(tm.session, id=1)
            user.name = "new name"
            tm.commit()

        # 或者使用 execute 方法
        with TransactionManager() as tm:
            result = tm.execute(
                action=lambda session: user_repository.create(data, session=session)
            )
    """

    def __init__(self):
        self.session: Session | None = None
        self._committed = False

    def __enter__(self):
        """进入上下文管理器，创建数据库会话"""
        self.session = SessionLocal()
        self._transaction = self.session.begin()
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if exc_type:
            if self.session:
                self.session.rollback()
            return False

        if not self._committed and self.session:
            self.session.commit()

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
    ) -> Any:
        """执行数据库操作

        Args:
            action: 数据库操作函数，接受session参数

        Returns:
            数据库操作的结果
        """
        result = action(self.session)
        self._committed = True
        self.session.commit()
        return result


def get_transaction_manager() -> TransactionManager:
    """获取TransactionManager实例（依赖注入函数）"""
    return TransactionManager()
