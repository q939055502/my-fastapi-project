from sqlalchemy import BigInteger, Column, Integer, String

from src.models.base import BaseModel, TimestampMixin


class FileMapping(BaseModel, TimestampMixin):
    """文件映射模型（文件管理）"""
    __tablename__ = "file_mapping"

    file_id = Column(String(255), unique=True, nullable=False, index=True, comment="文件ID")
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型")
    file_size = Column(BigInteger, nullable=True, comment="文件大小(字节)")
    file_path = Column(String(500), nullable=True, comment="本地文件路径")
    file_url = Column(String(500), nullable=True, comment="文件访问URL")

    storage_type = Column(String(20), default="local", comment="存储类型：local/oss/cos")
    bucket_name = Column(String(100), nullable=True, comment="存储桶名称")

    upload_user_id = Column(Integer, nullable=False, index=True, comment="上传用户ID")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")

    category = Column(String(50), nullable=True, comment="文件分类：avatar/logo/attachment/image/document")
    description = Column(String(500), nullable=True, comment="文件描述")
