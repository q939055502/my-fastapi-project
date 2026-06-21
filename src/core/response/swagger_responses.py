"""
OpenAPI 响应配置模块

提供 swagger_responses() 函数，根据业务码生成 Swagger 响应配置。
"""

from collections import defaultdict
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel

from src.core.annotations import InterfaceType
from src.core.response.response_msg import RESPONSE_MSG

T = TypeVar("T")


def _generate_example_data(model: type[BaseModel]) -> dict:
    """
    根据 Pydantic 模型生成示例数据

    :param model: Pydantic 模型类
    :return: 示例数据字典
    """
    schema = model.model_json_schema()
    return _generate_example_from_schema(schema, schema.get("$defs", {}))


def _generate_example_from_schema(schema: dict, defs: dict) -> dict:
    """
    从 JSON Schema 生成示例数据

    :param schema: JSON Schema 字典
    :param defs: $defs 引用定义
    :return: 示例数据字典
    """
    result = {}

    properties = schema.get("properties", {})
    for field_name, field_schema in properties.items():
        result[field_name] = _generate_example_value(field_schema, defs)

    return result


def _generate_example_value(schema: dict, defs: dict) -> any:
    """
    根据字段类型生成示例值

    :param schema: 字段的 JSON Schema
    :param defs: $defs 引用定义
    :return: 示例值
    """
    if "example" in schema:
        return schema["example"]

    if "default" in schema:
        return schema["default"]

    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        if ref_name in defs:
            return _generate_example_from_schema(defs[ref_name], defs)
        return None

    field_type = schema.get("type")
    if field_type == "string":
        return "example"
    elif field_type == "integer":
        return 1
    elif field_type == "number":
        return 1.0
    elif field_type == "boolean":
        return True
    elif field_type == "array":
        items = schema.get("items", {})
        return [_generate_example_value(items, defs)] if items else []
    elif field_type == "object":
        return _generate_example_from_schema(schema, defs)
    elif "anyOf" in schema:
        for option in schema["anyOf"]:
            if option.get("type") != "null":
                return _generate_example_value(option, defs)
        return None
    else:
        return None


def swagger_responses(
    codes: list[int],
    data_model: type[BaseModel] | None = None,
    is_pagination: bool = False,
    success_msg: str = "操作成功",
    interface_type: InterfaceType = InterfaceType.TENANT,
    code_model_map: dict[int, type[BaseModel]] | None = None,
) -> dict:
    """
    根据业务码生成 Swagger responses 配置

    :param codes: 业务码列表，如 [20000, 40001, 40104]
    :param data_model: 成功响应的数据模型（用于生成示例数据，作为默认模型）
    :param is_pagination: 是否分页响应
    :param success_msg: 成功响应的消息描述
    :param interface_type: 接口类型，PUBLIC 类型不显示 401/403 错误码
    :param code_model_map: 业务码到数据模型的映射，用于不同业务码返回不同数据结构
                          如 {20000: LoginResponse, 20007: LoginSelectUserResponse}
    :return: Swagger 标准响应格式
    """
    # 自动补充常见错误码
    common_codes = [
        # 资源不存在
        40400, 40401,
        # 参数校验失败（FastAPI Pydantic 验证）
        42200, 42201, 42202, 42203, 42204, 42205,
        # 限流
        42900, 42901,
        # 服务器错误
        50000, 50001, 50002, 50003,
    ]

    # 非公开接口需要认证和授权
    if interface_type != InterfaceType.PUBLIC:
        common_codes.extend([
            # 认证失败（401）
            40100, 40101, 40102, 40103, 40104,
            # 权限不足（403）
            40300, 40301, 40302, 40303,
        ])

    # 合并并去重（保持传入码的顺序）
    all_codes = list(dict.fromkeys(codes + common_codes))

    responses = {}

    grouped: dict[int, list[int]] = defaultdict(list)
    for code in all_codes:
        http_status = int(str(code)[:3])
        grouped[http_status].append(code)

    for http_status, code_list in grouped.items():
        if http_status in (200, 201, 204):
            responses[str(http_status)] = _build_success_response(
                http_status, code_list, data_model, is_pagination, success_msg, code_model_map
            )
        else:
            responses[str(http_status)] = _build_error_responses(http_status, code_list)

    return responses


def _build_success_response(
    http_status: int,
    codes: list[int],
    data_model: type[BaseModel] | None,
    is_pagination: bool,
    success_msg: str,
    code_model_map: dict[int, type[BaseModel]] | None = None,
) -> dict:
    """
    构建成功响应配置

    :param http_status: HTTP 状态码
    :param codes: 业务码列表
    :param data_model: 响应数据模型（默认模型）
    :param is_pagination: 是否分页
    :param success_msg: 成功消息
    :param code_model_map: 业务码到数据模型的映射
    """
    examples = {}

    # 生成每个业务码的示例
    for code in codes:
        msg = RESPONSE_MSG.get(code, success_msg)
        example_name = msg

        # 获取当前业务码对应的模型（优先使用 code_model_map，否则使用默认 data_model）
        current_model = None
        if code_model_map and code in code_model_map:
            current_model = code_model_map[code]
        elif data_model is not None:
            current_model = data_model

        # 构建 data 部分
        if current_model is not None:
            try:
                if is_pagination:
                    # 分页响应
                    data = {
                        "list": [_generate_example_data(current_model)],
                        "pagination": {
                            "total": 100,
                            "page": 1,
                            "page_size": 10,
                            "total_pages": 10
                        }
                    }
                else:
                    # 普通响应
                    data = _generate_example_data(current_model)
            except Exception:
                data = None
        else:
            data = None

        resp_data = {
            "code": code,
            "msg": msg,
            "data": data,
            "detail": None,
            "request_id": "abc-123",
            "timestamp": datetime.now().isoformat()
        }

        examples[example_name] = {"value": resp_data}

    return {
        "description": success_msg,
        "content": {
            "application/json": {
                "examples": examples
            }
        }
    }


def _build_error_responses(http_status: int, codes: list[int]) -> dict:
    """
    构建错误响应配置

    :param http_status: HTTP 状态码
    :param codes: 业务码列表
    """
    examples = {}

    for code in codes:
        msg = RESPONSE_MSG.get(code, "未知错误")
        example_name = msg

        resp_data = {
            "code": code,
            "msg": msg,
            "data": None,
            "detail": None,
            "request_id": "abc-123",
            "timestamp": datetime.now().isoformat()
        }

        examples[example_name] = {"value": resp_data}

    # 获取通用的 HTTP 状态码描述
    http_descriptions = {
        400: "请求参数错误或业务条件不满足",
        401: "未授权或登录已过期",
        403: "无访问权限",
        404: "资源不存在",
        409: "数据冲突",
        422: "参数校验失败",
        429: "请求过于频繁",
        500: "服务器内部错误",
    }
    description = http_descriptions.get(http_status, "请求处理失败")

    return {
        "description": description,
        "content": {
            "application/json": {
                "examples": examples
            }
        }
    }


# 以下为旧版函数，保留用于兼容
def gen_swagger_response(
    codes: list[int],
    description: str = "业务响应结果",
    example_data: dict | None = None,
    is_pagination: bool = False
) -> dict:
    """
    自动生成 Swagger 响应示例（旧版，保留兼容）

    :param codes: 业务码列表 [20000, 40401, ...]
    :param description: Swagger 描述
    :param example_data: 自定义示例数据(成功响应时使用)
    :param is_pagination: 是否分页响应
    :return: Swagger 标准响应格式
    """
    return swagger_responses(codes=codes, success_msg=description)
