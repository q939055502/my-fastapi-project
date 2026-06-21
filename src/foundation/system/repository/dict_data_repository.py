from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.core.storage import BaseRepository
from src.models.platform import DictData


class DictDataRepository(BaseRepository[DictData, None, None]):
    def __init__(self):
        super().__init__(model=DictData)

    def get_by_type_code(self, type_code: str, session: Session) -> list[DictData]:
        """根据字典类型编码获取字典数据"""
        query = select(DictData).join(
            DictData.dict_type
        ).where(
            and_(
                DictData.dict_type.has(code=type_code),
                DictData.dict_type.has(delete_time=None)  # DictType 需要手动过滤
            )
        )
        query = self._apply_soft_delete_filter(query)  # DictData 使用基类方法
        return list(session.execute(query).scalars().all())

    def get_by_type_id(self, type_id: int, session: Session) -> list[DictData]:
        """根据字典类型ID获取字典数据"""
        query = select(DictData).where(DictData.dict_type_id == type_id)
        query = self._apply_soft_delete_filter(query)
        return list(session.execute(query).scalars().all())

    def get_by_value(self, type_id: int, value: str, session: Session) -> DictData | None:
        """根据类型ID和值获取字典数据"""
        query = select(DictData).where(
            and_(
                DictData.dict_type_id == type_id,
                DictData.value == value
            )
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().first()


dict_data_repository = DictDataRepository()
