from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import FileResponse

from src.core.auth import AuthControl
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.models.iam import User
from src.services.system.file_service import file_service

router = APIRouter(
    tags=["通用-文件管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/upload",
    summary="文件上传",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="文件类型或大小不符合要求"
        ),
    },
)
@apply_rate_limit("20/minute")
def upload_file(
    request: Request,
    file: UploadFile = File(...),
    file_type: str = Query("default", description="文件类型"),
    current_user: User = Depends(AuthControl.is_authed),
):
    result = file_service.upload_file(file, user_id=current_user.id)
    return success(data=result.data)


@router.get(
    "/download",
    summary="文件下载",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="文件不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def download_file(request: Request, file_id: str = Query(..., description="文件ID")):
    file_info = file_service.get_file_info(file_id)
    if not file_info:
        return {"code": -1, "msg": "文件不存在"}
    return FileResponse(file_info["file_path"], filename=file_info["original_name"])
