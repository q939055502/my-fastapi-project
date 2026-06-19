"""�����������Transaction Manager��

�ṩ�����������������ȷ�����ݿ������ԭ���ԡ�
"""

from collections.abc import Callablefrom contextlib import contextmanagerfrom typing import Anyfrom sqlalchemy.orm import Sessionfrom .database import SessionLocalclass TransactionManager:
    """���������

    ͳһ�������ݿ�Ự�����������ȷ������һ���ԡ�

    ʹ�÷�ʽ��
        with TransactionManager() as tm:
            user = user_repository.get(tm.session, id=1)
            user.name = "new name"
            tm.commit()

        # ����ʹ�� execute ����
        with TransactionManager() as tm:
            result = tm.execute(
                action=lambda session: user_repository.create(data, session=session)
            )
    """

    def __init__(self):
        self.session: Session | None = None
        self._committed = False

    def __enter__(self):
        """���������Ĺ��������������ݿ�Ự"""
        self.session = SessionLocal()
        self._transaction = self.session.begin()
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """�˳������Ĺ�����"""
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
        """�ύ����"""
        if self.session:
            self.session.commit()
            self._committed = True

    def rollback(self):
        """�ع�����"""
        if self.session:
            self.session.rollback()
            self._committed = True

    @contextmanager
    def transaction(self):
        """Ƕ�����������Ĺ�����"""
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
        """ִ�����ݿ����

        Args:
            action: ���ݿ��������������session����

        Returns:
            ���ݿ�����Ľ��
        """
        result = action(self.session)
        self._committed = True
        self.session.commit()
        return result


def get_transaction_manager() -> TransactionManager:
    """��ȡTransactionManagerʵ��������ע�뺯����"""
    return TransactionManager()
