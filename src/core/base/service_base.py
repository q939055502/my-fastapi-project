
from sqlalchemy.orm import Session

from src.core.storage.uuid_resolver import uuid_resolver


class BaseService:
    """Service 基类 - 提供通用工具方法"""

    def get_id_by_uuid(self, table_name: str, uuid: str, session: Session) -> int | None:
        """UUID 转 ID 单个转换"""
        return uuid_resolver.resolve(session, table_name, uuid)

    def get_ids_by_uuids(self, table_name: str, uuids: list[str], session: Session) -> list[int | None]:
        """UUID 转 ID 批量转换"""
        return uuid_resolver.resolve(session, table_name, uuids)
