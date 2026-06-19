def swagger_responses(
    codes: list[int],
    response_model: type[BaseModel] | None = None,
    is_pagination: bool = False,
    success_msg: str = "操作成功",
) -> dict:
    """
    根据业务码生成 Swagger responses 配置
    
    :param codes: 业务码列表，如 [20000, 40001, 40104]
    :param response_model: 成功响应的数据模型
    :param is_pagination: 是否分页响应
    :param success_msg: 成功响应的消息描述
    """
    responses = {}
    
    for code in codes:
        http_status = int(str(code)[:3])  # 业务码 → HTTP 状态码
        msg = RESPONSE_MSG.get(code, "未知错误")
        
        # 构建响应配置...
        
    return responses


auth_v1_router.post("/refresh")(public_api(refresh_access_token))


# 步骤1：auth_v1_router.post("/refresh") 返回一个 APIRoute 对象
route = auth_v1_router.post("/refresh")
print(type(route))  # <class 'fastapi.routing.APIRoute'>

# 步骤2：调用这个 route 对象，传入函数
route(public_api(refresh_access_token))


