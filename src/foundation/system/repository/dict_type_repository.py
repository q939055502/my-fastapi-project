from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload
from src.core.storage import BaseRepository
from src.models.platform import DictType


class DictTypeRepository(BaseRepository[DictType, None, None]):
    def __init__(self):
        super().__init__(model=DictType)

    def get_by_code(self, code: str, session: Session) -> DictType | None:
        """根据编码获取字典类型"""
        query = select(DictType).where(DictType.code == code)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().first()

    def get_with_data(self, code: str, session: Session) -> DictType | None:
        """获取字典类型及其数据"""
        query = select(DictType).where(DictType.code == code)
        query = self._apply_soft_delete_filter(query)
        query = query.options(joinedload(DictType.datas))
        return session.execute(query).scalars().first()

    def is_code_exists(self, code: str, exclude_id: int = None, session: Session = None) -> bool:
        """检查编码是否存在"""
        query = select(DictType).where(DictType.code == code)
        query = self._apply_soft_delete_filter(query)
        if exclude_id:
            query = query.where(DictType.id != exclude_id)
        return session.execute(query).scalars().first() is not None


dict_type_repository = DictTypeRepository()