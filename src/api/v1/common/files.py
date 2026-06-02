from fastapi import APIRouter, File, Query, Request, UploadFile
from fastapi.responses import FileResponse

from src.core.handlers import success
from src.core.plugins import apply_rate_limit
from src.services.sys.file_mapping_service import file_service

router = APIRouter(tags=["通用-文件管理"])


@router.post("/upload", summary="文件上传")
@apply_rate_limit("20/minute")
def upload_file(request: Request, file: UploadFile = File(...), file_type: str = Query("default", description="文件类型")):
    result = file_service.upload_file(file)
    return success(data=result.data)


@router.get("/download", summary="文件下载")
@apply_rate_limit("60/minute")
def download_file(request: Request, file_id: str = Query(..., description="文件ID")):
    file_info = file_service.get_file_info(file_id)
    if not file_info:
        return {"code": -1, "msg": "文件不存在"}
    return FileResponse(file_info["file_path"], filename=file_info["original_name"])
