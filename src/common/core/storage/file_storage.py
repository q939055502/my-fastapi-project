from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urljoin

from src.common.core.config import settings
from src.common.core.log import logger


class StorageBackend(ABC):
    @abstractmethod
    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None
    ) -> str:
        """上传文件

        Args:
            file: 文件对象
            key: 文件唯一标识（如 "avatars/user_123.jpg")
            content_type: 文件 MIME 类型

        Returns:
            str: 文件访问路径/URL
        """
        pass

    @abstractmethod
    def download(self, key: str) -> BinaryIO:
        """下载文件"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """获取文件访问链接

        Args:
            key: 文件唯一标识
            expires_in: 链接有效期（秒），仅对私有存储有效

        Returns:
            str: 文件访问 URL
        """
        pass


class LocalStorage(StorageBackend):
    def __init__(self, base_dir: str, base_url: str):
        self.base_dir = Path(base_dir)
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"本地存储目录初始化成功: {self.base_dir}")
        except Exception as e:
            logger.error(f"本地存储目录初始化失败: {str(e)}")
            raise
        self.base_url = base_url

    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None
    ) -> str:
        try:
            file_path = self.base_dir / key
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(file.read())

            logger.info(f"文件上传成功: {key}")
            return self.get_url(key)
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise

    def download(self, key: str) -> BinaryIO:
        try:
            file_path = self.base_dir / key
            if not file_path.exists():
                logger.error(f"文件不存在: {key}")
                raise FileNotFoundError(f"File not found: {key}")

            logger.info(f"文件下载成功: {key}")
            return open(file_path, "rb")
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            raise

    def delete(self, key: str) -> bool:
        try:
            file_path = self.base_dir / key
            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件删除成功: {key}")
                return True
            logger.warning(f"文件不存在，无法删除: {key}")
            return False
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            url = urljoin(self.base_url, key)
            logger.debug(f"获取文件URL: {url}")
            return url
        except Exception as e:
            logger.error(f"获取文件URL失败: {str(e)}")
            raise


try:
    import oss2

    class OSSStorage(StorageBackend):
        def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, bucket_name: str):
            try:
                self.auth = oss2.Auth(access_key_id, access_key_secret)
                self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
                logger.info("阿里云 OSS 存储初始化成功")
            except Exception as e:
                logger.error(f"阿里云 OSS 存储初始化失败: {str(e)}")
                raise

        def upload(
            self,
            file: BinaryIO,
            key: str,
            content_type: str | None = None
        ) -> str:
            try:
                file.seek(0)
                self.bucket.put_object(key, file.read(), content_type=content_type)
                logger.info(f"文件上传到 OSS 成功: {key}")
                return self.get_url(key)
            except Exception as e:
                logger.error(f"文件上传到 OSS 失败: {str(e)}")
                raise

        def download(self, key: str) -> BinaryIO:
            try:
                import io
                result = self.bucket.get_object(key)
                content = result.read()
                logger.info(f"文件从 OSS 下载成功: {key}")
                return io.BytesIO(content)
            except oss2.exceptions.NoSuchKey:
                logger.error(f"文件在 OSS 中不存在: {key}")
                raise FileNotFoundError(f"File not found: {key}") from None
            except Exception as e:
                logger.error(f"文件从 OSS 下载失败: {str(e)}")
                raise

        def delete(self, key: str) -> bool:
            try:
                self.bucket.delete_object(key)
                logger.info(f"文件从 OSS 删除成功: {key}")
                return True
            except oss2.exceptions.NoSuchKey:
                logger.warning(f"文件在 OSS 中不存在，无法删除: {key}")
                return False
            except Exception as e:
                logger.error(f"文件从 OSS 删除失败: {str(e)}")
                return False

        def get_url(self, key: str, expires_in: int = 3600) -> str:
            try:
                url = self.bucket.sign_url('GET', key, expires_in)
                logger.debug(f"获取 OSS 文件URL: {url}")
                return url
            except Exception as e:
                logger.error(f"获取 OSS 文件URL失败: {str(e)}")
                raise
except ImportError:
    logger.warning("未安装阿里云 OSS SDK，OSS 存储功能不可用")
    OSSStorage = None


try:
    from qcloud_cos import CosConfig, CosS3Client

    class COSStorage(StorageBackend):
        def __init__(self, secret_id: str, secret_key: str, region: str, bucket_name: str):
            try:
                config = CosConfig(
                    Region=region,
                    SecretId=secret_id,
                    SecretKey=secret_key
                )
                self.client = CosS3Client(config)
                self.bucket_name = bucket_name
                logger.info("腾讯云 COS 存储初始化成功")
            except Exception as e:
                logger.error(f"腾讯云 COS 存储初始化失败: {str(e)}")
                raise

        def upload(
            self,
            file: BinaryIO,
            key: str,
            content_type: str | None = None
        ) -> str:
            try:
                file.seek(0)
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file.read(),
                    ContentType=content_type or 'application/octet-stream'
                )
                logger.info(f"文件上传到 COS 成功: {key}")
                return self.get_url(key)
            except Exception as e:
                logger.error(f"文件上传到 COS 失败: {str(e)}")
                raise

        def download(self, key: str) -> BinaryIO:
            try:
                import io
                response = self.client.get_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                content = response['Body'].read()
                logger.info(f"文件从 COS 下载成功: {key}")
                return io.BytesIO(content)
            except Exception as e:
                    if 'NoSuchKey' in str(e):
                        logger.error(f"文件在 COS 中不存在: {key}")
                        raise FileNotFoundError(f"File not found: {key}") from None
                    logger.error(f"文件从 COS 下载失败: {str(e)}")
                    raise

        def delete(self, key: str) -> bool:
            try:
                self.client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info(f"文件从 COS 删除成功: {key}")
                return True
            except Exception as e:
                if 'NoSuchKey' in str(e):
                    logger.warning(f"文件在 COS 中不存在，无法删除: {key}")
                    return False
                logger.error(f"文件从 COS 删除失败: {str(e)}")
                return False

        def get_url(self, key: str, expires_in: int = 3600) -> str:
            try:
                url = self.client.get_presigned_url(
                    Method='GET',
                    Bucket=self.bucket_name,
                    Key=key,
                    Expires=expires_in
                )
                logger.debug(f"获取 COS 文件URL: {url}")
                return url
            except Exception as e:
                logger.error(f"获取 COS 文件URL失败: {str(e)}")
                raise
except ImportError:
    logger.warning("未安装腾讯云 COS SDK，COS 存储功能不可用")
    COSStorage = None


def get_storage_backend() -> StorageBackend:
    """根据配置获取存储后端实例

    Returns:
        StorageBackend: 存储后端实例
    """
    try:
        storage_type = settings.STORAGE_TYPE.lower()

        if storage_type == "local":
            return LocalStorage(
                base_dir=settings.LOCAL_STORAGE_DIR,
                base_url=settings.LOCAL_STORAGE_URL
            )
        elif storage_type == "oss" and OSSStorage:
            return OSSStorage(
                access_key_id=settings.OSS_ACCESS_KEY_ID,
                access_key_secret=settings.OSS_ACCESS_KEY_SECRET,
                endpoint=settings.OSS_ENDPOINT,
                bucket_name=settings.OSS_BUCKET_NAME
            )
        elif storage_type == "cos" and COSStorage:
            return COSStorage(
                secret_id=settings.COS_SECRET_ID,
                secret_key=settings.COS_SECRET_KEY,
                region=settings.COS_REGION,
                bucket_name=settings.COS_BUCKET_NAME
            )
        else:
            logger.warning(f"不支持的存储类型: {storage_type}，默认使用本地存储")
            return LocalStorage(
                base_dir=settings.LOCAL_STORAGE_DIR,
                base_url=settings.LOCAL_STORAGE_URL
            )
    except Exception as e:
        logger.error(f"初始化存储后端失败: {str(e)}")
        logger.warning("存储后端初始化失败，默认使用本地存储")
        return LocalStorage(
            base_dir=settings.LOCAL_STORAGE_DIR,
            base_url=settings.LOCAL_STORAGE_URL
        )


try:
    storage: StorageBackend = get_storage_backend()
    logger.info("存储服务初始化成功")
except Exception as e:
    logger.error(f"存储服务初始化失败: {str(e)}")
    logger.warning("存储服务初始化失败，默认使用本地存储")
    storage: StorageBackend = LocalStorage(
        base_dir=settings.LOCAL_STORAGE_DIR,
        base_url=settings.LOCAL_STORAGE_URL
    )
