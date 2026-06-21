"""
字典数据管理接口(超级管理员专用)
"""

from uuid import UUID

from fastapi import APIRouter, Request

from src.core.exceptions import BusinessException
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse
from src.core.storage import TransactionManager
from src.core.storage.uuid_resolver import uuid_resolver
from src.foundation.system.repository.dict_data_repository import dict_data_repository
from src.foundation.system.repository.dict_type_repository import dict_type_repository
from src.foundation.system.schemas.dict_data import (
    DictDataCreate,
    DictDataResponse,
    DictDataUpdate,
)
from src.foundation.system.schemas.dict_type import (
    DictTypeCreate,
    DictTypeResponse,
    DictTypeUpdate,
)

router = APIRouter(
    tags=["平台管理-字典"],
)


@router.get("/types", summary="获取字典类型列表")
@apply_rate_limit("60/minute")
def list_dict_types(request: Request) -> ApiResponse[list[DictTypeResponse]]:
    with TransactionManager() as tm:
        total, types = dict_type_repository.list(session=tm.session)
        type_responses = [DictTypeResponse.model_validate(t) for t in types]
        return ApiResponse(code=20000, msg="操作成功", data=type_responses)


@router.get("/types/{type_uuid}", summary="获取字典类型详情")
@apply_rate_limit("60/minute")
def get_dict_type(request: Request, type_uuid: UUID) -> ApiResponse[DictTypeResponse]:
    with TransactionManager() as tm:
        type_id = uuid_resolver.resolve(tm.session, "dict_type", str(type_uuid))
        if not type_id:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_type = dict_type_repository.get(id=type_id, session=tm.session)
        if not dict_type:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_type_response = DictTypeResponse.model_validate(dict_type)
        return ApiResponse(code=20000, msg="操作成功", data=dict_type_response)


@router.post("/types", summary="创建字典类型")
@apply_rate_limit("30/minute")
def create_dict_type(request: Request, type_in: DictTypeCreate) -> ApiResponse[DictTypeResponse]:
    with TransactionManager() as tm:
        if dict_type_repository.is_code_exists(type_in.code, session=tm.session):
            raise BusinessException(40000, detail="字典类型编码已存在")
        new_type = dict_type_repository.create(obj_in=type_in, session=tm.session)
        tm.commit()
        dict_type_response = DictTypeResponse.model_validate(new_type)
        return ApiResponse(code=20000, msg="字典类型创建成功", data=dict_type_response)


@router.put("/types/{type_uuid}", summary="更新字典类型")
@apply_rate_limit("30/minute")
def update_dict_type(request: Request, type_uuid: UUID, type_in: DictTypeUpdate) -> ApiResponse[None]:
    with TransactionManager() as tm:
        type_id = uuid_resolver.resolve(tm.session, "dict_type", str(type_uuid))
        if not type_id:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_type = dict_type_repository.get(id=type_id, session=tm.session)
        if not dict_type:
            raise BusinessException(40401, detail="字典类型不存在")
        if type_in.code and type_in.code != dict_type.code:
            if dict_type_repository.is_code_exists(type_in.code, exclude_id=dict_type.id, session=tm.session):
                raise BusinessException(40000, detail="字典类型编码已存在")
        dict_type_repository.update(id=dict_type.id, obj_in=type_in, session=tm.session)
        tm.commit()
        return ApiResponse(code=20000, msg="字典类型更新成功")


@router.delete("/types/{type_uuid}", summary="删除字典类型")
@apply_rate_limit("30/minute")
def delete_dict_type(request: Request, type_uuid: UUID) -> ApiResponse[None]:
    with TransactionManager() as tm:
        type_id = uuid_resolver.resolve(tm.session, "dict_type", str(type_uuid))
        if not type_id:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_type = dict_type_repository.get(id=type_id, session=tm.session)
        if not dict_type:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_type_repository.delete(id=dict_type.id, session=tm.session)
        tm.commit()
        return ApiResponse(code=20000, msg="字典类型删除成功")


@router.get("/data/{type_code}", summary="根据字典类型编码获取字典数据")
@apply_rate_limit("60/minute")
def get_dict_data_by_type(request: Request, type_code: str) -> ApiResponse[list[DictDataResponse]]:
    with TransactionManager() as tm:
        dict_datas = dict_data_repository.get_by_type_code(type_code, session=tm.session)
        data_responses = [DictDataResponse.model_validate(d) for d in dict_datas]
        return ApiResponse(code=20000, msg="操作成功", data=data_responses)


@router.get("/data/list/{type_uuid}", summary="获取字典数据列表")
@apply_rate_limit("60/minute")
def list_dict_data(request: Request, type_uuid: UUID) -> ApiResponse[list[DictDataResponse]]:
    with TransactionManager() as tm:
        type_id = uuid_resolver.resolve(tm.session, "dict_type", str(type_uuid))
        if not type_id:
            raise BusinessException(40401, detail="字典类型不存在")
        dict_datas = dict_data_repository.get_by_type_id(type_id, session=tm.session)
        data_responses = [DictDataResponse.model_validate(d) for d in dict_datas]
        return ApiResponse(code=20000, msg="操作成功", data=data_responses)


@router.post("/data", summary="创建字典数据")
@apply_rate_limit("30/minute")
def create_dict_data(request: Request, data_in: DictDataCreate) -> ApiResponse[DictDataResponse]:
    with TransactionManager() as tm:
        type_id = uuid_resolver.resolve(tm.session, "dict_type", str(data_in.dict_type_uuid))
        if not type_id:
            raise BusinessException(40401, detail="字典类型不存在")
        data_in_dict = data_in.model_dump()
        data_in_dict["dict_type_id"] = type_id
        data_in_dict.pop("dict_type_uuid")
        new_data = dict_data_repository.create(obj_in=data_in_dict, session=tm.session)
        tm.commit()
        data_response = DictDataResponse.model_validate(new_data)
        return ApiResponse(code=20000, msg="字典数据创建成功", data=data_response)


@router.put("/data/{data_uuid}", summary="更新字典数据")
@apply_rate_limit("30/minute")
def update_dict_data(request: Request, data_uuid: UUID, data_in: DictDataUpdate) -> ApiResponse[None]:
    with TransactionManager() as tm:
        data_id = uuid_resolver.resolve(tm.session, "dict_data", str(data_uuid))
        if not data_id:
            raise BusinessException(40401, detail="字典数据不存在")
        dict_data = dict_data_repository.get(id=data_id, session=tm.session)
        if not dict_data:
            raise BusinessException(40401, detail="字典数据不存在")
        update_data = data_in.model_dump(exclude_unset=True)
        if "dict_type_uuid" in update_data:
            type_id = uuid_resolver.resolve(tm.session, "dict_type", str(update_data["dict_type_uuid"]))
            if not type_id:
                raise BusinessException(40401, detail="字典类型不存在")
            update_data["dict_type_id"] = type_id
            update_data.pop("dict_type_uuid")
        dict_data_repository.update(id=dict_data.id, obj_in=update_data, session=tm.session)
        tm.commit()
        return ApiResponse(code=20000, msg="字典数据更新成功")


@router.delete("/data/{data_uuid}", summary="删除字典数据")
@apply_rate_limit("30/minute")
def delete_dict_data(request: Request, data_uuid: UUID) -> ApiResponse[None]:
    with TransactionManager() as tm:
        data_id = uuid_resolver.resolve(tm.session, "dict_data", str(data_uuid))
        if not data_id:
            raise BusinessException(40401, detail="字典数据不存在")
        dict_data = dict_data_repository.get(id=data_id, session=tm.session)
        if not dict_data:
            raise BusinessException(40401, detail="字典数据不存在")
        dict_data_repository.delete(id=dict_data.id, session=tm.session)
        tm.commit()
        return ApiResponse(code=20000, msg="字典数据删除成功")
