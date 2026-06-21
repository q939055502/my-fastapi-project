"""文件映射仓库 - 管理文件ID和文件信息的映射关系"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.storage import BaseRepository
from src.models.platform import FileMapping


class FileMappingCreate:
    """文件映射创建模型"""

    def __init__(
        self,
        file_id: str,
        original_name: str,
        file_type: str,
        file_size: int | None,
        user_id: int,
        agent_id: int | None = None,
    ):
        self.file_id = file_id
        self.original_name = original_name
        self.file_type = file_type
        self.file_size = file_size
        self.user_id = user_id
        self.agent_id = agent_id


class FileMappingUpdate:
    """文件映射更新模型"""

    pass


class FileMappingRepository(
    BaseRepository[FileMapping, FileMappingCreate, FileMappingUpdate]
):
    """文件映射仓库"""
    def __init__(self):
        super().__init__(model=FileMapping)

    def create_file_mapping(
        self,
        file_id: str,
        original_name: str,
        file_type: str,
        file_size: int | None,
        user_id: int,
        file_path: str | None = None,
        session: Session = None,
    ) -> FileMapping:
        """创建文件映射记录"""
        file_mapping = FileMapping(
            file_id=file_id,
            original_filename=original_name,
            file_type=file_type,
            file_size=file_size,
            upload_user_id=user_id,
            file_path=file_path,
        )
        session.add(file_mapping)
        session.flush()
        session.refresh(file_mapping)
        return file_mapping

    def get_file_info_by_ids(self, file_ids: list[str], session: Session) -> list[FileMapping]:
        """根据文件ID列表获取文件信息"""
        if not file_ids:
            return []

        result = session.execute(
            select(FileMapping).where(FileMapping.file_id.in_(file_ids))
        )
        return result.scalars().all()

    def get_file_mapping_by_file_id(self, file_id: str, session: Session) -> dict | None:
        """根据文件ID获取文件映射信息"""
        result = session.execute(
            select(FileMapping).where(FileMapping.file_id == file_id)
        )
        mapping = result.scalars().first()
        if mapping:
            return {
                "file_id": mapping.file_id,
                "original_filename": mapping.original_filename,
                "file_type": mapping.file_type,
                "file_size": mapping.file_size,
                "upload_user_id": mapping.upload_user_id,
                "file_path": mapping.file_path,
            }
        return None


file_mapping_repository = FileMappingRepository()
