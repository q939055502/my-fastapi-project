"""
字典数据管理接口（超级管理员专用）
"""

from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success, success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.schemas.dict_data import DictDataCreate, DictDataUpdate
from src.foundation.system.schemas.dict_type import DictTypeCreate, DictTypeUpdate
from src.foundation.system.repository.dict_data_repository import dict_data_repository
from src.foundation.system.repository.dict_type_repository import dict_type_repository
from src.core.storage import TransactionManager

router = APIRouter(
    tags=["平台管理-字典"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/types", summary="获取字典类型列表")
@apply_rate_limit("60/minute")
def list_dict_types(request: Request):
    with TransactionManager() as tm:
        total, types = dict_type_repository.list(session=tm.session)
        return success_page(data=[t.to_dict() for t in types], total=total, page=1, page_size=total)


@router.get("/types/{type_uuid}", summary="获取字典类型详情")
@apply_rate_limit("60/minute")
def get_dict_type(request: Request, type_uuid: UUID):
    with TransactionManager() as tm:
        dict_type = dict_type_repository.get_by_uuid(uuid=type_uuid, session=tm.session)
        if not dict_type:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
        return success(data=dict_type.to_dict())


@router.post("/types", summary="创建字典类型")
@apply_rate_limit("30/minute")
def create_dict_type(request: Request, type_in: DictTypeCreate):
    with TransactionManager() as tm:
        if dict_type_repository.is_code_exists(type_in.code, session=tm.session):
            raise BusinessException(ResponseCode.PARAM_ERROR, detail="字典类型编码已存在")
        new_type = dict_type_repository.create(obj_in=type_in, session=tm.session)
        tm.commit()
        return success(data=new_type.to_dict(), msg="字典类型创建成功")


@router.put("/types/{type_uuid}", summary="更新字典类型")
@apply_rate_limit("30/minute")
def update_dict_type(request: Request, type_uuid: UUID, type_in: DictTypeUpdate):
    with TransactionManager() as tm:
        dict_type = dict_type_repository.get_by_uuid(uuid=type_uuid, session=tm.session)
        if not dict_type:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
        if type_in.code and type_in.code != dict_type.code:
            if dict_type_repository.is_code_exists(type_in.code, exclude_id=dict_type.id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, detail="字典类型编码已存在")
        dict_type_repository.update(id=dict_type.id, obj_in=type_in, session=tm.session)
        tm.commit()
        return success(msg="字典类型更新成功")


@router.delete("/types/{type_uuid}", summary="删除字典类型")
@apply_rate_limit("30/minute")
def delete_dict_type(request: Request, type_uuid: UUID):
    with TransactionManager() as tm:
        dict_type = dict_type_repository.get_by_uuid(uuid=type_uuid, session=tm.session)
        if not dict_type:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
        dict_type_repository.delete(id=dict_type.id, session=tm.session)
        tm.commit()
        return success(msg="字典类型删除成功")


@router.get("/data/{type_code}", summary="根据字典类型编码获取字典数据")
@apply_rate_limit("60/minute")
def get_dict_data_by_type(request: Request, type_code: str):
    with TransactionManager() as tm:
        dict_datas = dict_data_repository.get_by_type_code(type_code, session=tm.session)
        return success(data=[d.to_dict() for d in dict_datas])


@router.get("/data/list/{type_uuid}", summary="获取字典数据列表")
@apply_rate_limit("60/minute")
def list_dict_data(request: Request, type_uuid: UUID):
    with TransactionManager() as tm:
        dict_type = dict_type_repository.get_by_uuid(uuid=type_uuid, session=tm.session)
        if not dict_type:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
        dict_datas = dict_data_repository.get_by_type_id(dict_type.id, session=tm.session)
        return success(data=[d.to_dict() for d in dict_datas])


@router.post("/data", summary="创建字典数据")
@apply_rate_limit("30/minute")
def create_dict_data(request: Request, data_in: DictDataCreate):
    with TransactionManager() as tm:
        dict_type = dict_type_repository.get_by_uuid(uuid=data_in.dict_type_uuid, session=tm.session)
        if not dict_type:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
        data_in_dict = data_in.model_dump()
        data_in_dict["dict_type_id"] = dict_type.id
        data_in_dict.pop("dict_type_uuid")
        new_data = dict_data_repository.create(obj_in=data_in_dict, session=tm.session)
        tm.commit()
        return success(data=new_data.to_dict(), msg="字典数据创建成功")


@router.put("/data/{data_uuid}", summary="更新字典数据")
@apply_rate_limit("30/minute")
def update_dict_data(request: Request, data_uuid: UUID, data_in: DictDataUpdate):
    with TransactionManager() as tm:
        dict_data = dict_data_repository.get_by_uuid(uuid=data_uuid, session=tm.session)
        if not dict_data:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典数据不存在")
        update_data = data_in.model_dump(exclude_unset=True)
        if "dict_type_uuid" in update_data:
            dict_type = dict_type_repository.get_by_uuid(uuid=update_data["dict_type_uuid"], session=tm.session)
            if not dict_type:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典类型不存在")
            update_data["dict_type_id"] = dict_type.id
            update_data.pop("dict_type_uuid")
        dict_data_repository.update(id=dict_data.id, obj_in=update_data, session=tm.session)
        tm.commit()
        return success(msg="字典数据更新成功")


@router.delete("/data/{data_uuid}", summary="删除字典数据")
@apply_rate_limit("30/minute")
def delete_dict_data(request: Request, data_uuid: UUID):
    with TransactionManager() as tm:
        dict_data = dict_data_repository.get_by_uuid(uuid=data_uuid, session=tm.session)
        if not dict_data:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="字典数据不存在")
        dict_data_repository.delete(id=dict_data.id, session=tm.session)
        tm.commit()
        return success(msg="字典数据删除成功")