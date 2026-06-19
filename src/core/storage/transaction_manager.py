"""Transaction manager for database operations"""

from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from .database import SessionLocal


class TransactionManager:
    """
    事务管理器，支持上下文管理和手动事务控制

    使用示例:
        with TransactionManager() as tm:
            user = user_repository.get(tm.session, id=1)
            user.name = "new name"
            tm.commit()

        with TransactionManager() as tm:
            result = tm.execute(
                action=lambda session: user_repository.create(data, session=session)
            )
    """

    def __init__(self):
        self.session: Session | None = None
        self._committed = False

    def __enter__(self):
        """进入上下文，创建数据库会话和事务"""
        self.session = SessionLocal()
        self._transaction = self.session.begin()
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，自动提交或回滚"""
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
        """手动提交事务"""
        if self.session:
            self.session.commit()
            self._committed = True

    def rollback(self):
        """手动回滚事务"""
        if self.session:
            self.session.rollback()
            self._committed = True

    @contextmanager
    def transaction(self):
        """创建嵌套事务"""
        nested_transaction = self.session.begin_nested()
        try:
            yield nested_transaction
        except Exception:
            nested_transaction.rollback()
            raise

    def execute(self, action: Callable[[Session], Any]) -> Any:
        """
        执行操作并自动提交

        Args:
            action: 接收 session 的回调函数

        Returns:
            action 的返回值
        """
        result = action(self.session)
        self._committed = True
        self.session.commit()
        return result


def get_transaction_manager() -> TransactionManager:
    """获取事务管理器实例"""
    return TransactionManager()
