import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from src.core.auth import CTX_USER_ID
from src.core.constants import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
)
from src.core.log import logger
from src.core.storage import UnitOfWork
from src.repositories.sys.file_mapping_repository import file_mapping_repository
from src.repositories.sys.user_repository import user_repository
from src.schemas.base import Success

MAX_FILE_SIZE = 500 * 1024 * 1024
UPLOADS_DIR = "uploads"

ALLOWED_EXTENSIONS: set[str] = {
    ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
    ".json", ".xml", ".csv", ".zip", ".rar", ".7z",
}

DANGEROUS_EXTENSIONS: set[str] = {
    ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs", ".js",
    ".jar", ".sh", ".ps1", ".php", ".asp", ".jsp", ".py", ".pl", ".rb",
}


class FileService:
    def __init__(self):
        self.logger = logger
        self.uploads_dir = Path(UPLOADS_DIR)
        self.uploads_dir.mkdir(exist_ok=True)

    def upload_file(self, file: UploadFile) -> Success:
        try:
            with UnitOfWork() as uow:
                user = self._authenticate_user(uow.session)

                self._validate_file_security(file)

                safe_filename = self._generate_safe_filename(file.filename)

                content = self._read_and_validate_file(file)

                file_id = str(uuid.uuid4())
                file_path = self.uploads_dir / f"{file_id}_{safe_filename}"

                with open(file_path, "wb") as f:
                    f.write(content)

                self.logger.info(f"文件已保存 {file_path}")

                self._save_file_mapping(
                    {"file_id": file_id, "file_path": str(file_path)}, file, user.id, uow.session
                )

                uow.commit()

            response_data = {
                "file_id": file_id,
                "original_filename": file.filename,
                "file_type": self._determine_file_type(file.filename),
                "file_size": len(content),
                "file_path": str(file_path),
            }

            return Success(
                data=response_data,
                msg="文件上传成功",
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"文件上传失败: {str(e)}")
            raise HTTPException(status_code=HTTP_INTERNAL_SERVER_ERROR, detail="文件上传失败") from e

    def _authenticate_user(self, session):
        user_id = CTX_USER_ID.get()
        if not user_id:
            raise HTTPException(status_code=HTTP_UNAUTHORIZED, detail="Authentication Required")

        user = user_repository.get(user_id, session=session)
        if not user:
            raise HTTPException(status_code=HTTP_NOT_FOUND, detail="用户不存在")

        return user

    def _validate_file_security(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="文件名不能为空")

        file_ext = Path(file.filename).suffix.lower()

        if file_ext in DANGEROUS_EXTENSIONS:
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST, detail=f"不允许上传的文件类型: {file_ext}"
            )

        if file_ext and file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST,
                detail=f"不支持的文件类型: {file_ext}，允许的类型: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

    def _generate_safe_filename(self, original_filename: str) -> str:
        file_ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4().hex}{file_ext}"

    def _read_and_validate_file(self, file: UploadFile) -> bytes:
        content = file.file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST,
                detail=f"文件大小超过限制 {MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        return content

    def _save_file_mapping(
        self,
        response_data: dict,
        file: UploadFile,
        user_id: int,
        session,
    ) -> None:
        try:
            file_id = response_data.get("file_id")
            if not file_id:
                self.logger.warning("无法从响应中获取文件ID")
                return

            file_type = self._determine_file_type(file.filename)

            file_size = file.size if hasattr(file, "size") else None

            file_mapping_repository.create_file_mapping(
                file_id=file_id,
                original_name=file.filename,
                file_type=file_type,
                file_size=file_size,
                user_id=user_id,
                file_path=response_data.get("file_path"),
                session=session,
            )

            self.logger.info(f"已保存文件映射 {file_id} -> {file.filename}")

        except Exception as e:
            self.logger.warning(f"保存文件映射失败: {str(e)}")

    def _determine_file_type(self, filename: str) -> str:
        if not filename:
            return "unknown"

        file_ext = filename.lower().split(".")[-1] if "." in filename else ""

        image_exts = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]
        audio_exts = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
        video_exts = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"]

        if file_ext in image_exts:
            return "image"
        elif file_ext in audio_exts:
            return "audio"
        elif file_ext in video_exts:
            return "video"
        else:
            return "document"


file_service = FileService()
