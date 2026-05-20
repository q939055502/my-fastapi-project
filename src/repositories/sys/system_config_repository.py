from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.storage.generic_repository import GenericRepository
from src.models.sys.system_config import SystemConfig


class SystemConfigRepository(GenericRepository):
    def __init__(self):
        super().__init__(model=SystemConfig)

    def get_by_code(self, code: str, session: Session) -> SystemConfig:
        """根据编码获取配置"""
        query = select(SystemConfig).where(SystemConfig.code == code)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()


system_config_repository = SystemConfigRepository()
