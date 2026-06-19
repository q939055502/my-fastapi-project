from src.core.response import ApiResponse
from src.foundation.system.schemas.user import UserResponse

@router.get("/users/{user_id}")
def get_user(user_id: int) -> ApiResponse[UserResponse]:
    user = user_service.get_user(user_id)
    return ApiResponse(
        code=ResponseCode.SUCCESS,
        msg="查询成功",
        data=user  # ORM -> Schema 自动转换
    )
    