from fastapi import APIRouter, Query, Request

from src.services.sys.dept_service import dept_service
from src.core.response import success
from src.schemas.sys.depts import *
from src.core.rate_limit import apply_rate_limit

router = APIRouter()


@router.post("/", summary="创建部门")
@apply_rate_limit("30/minute")
def create_dept(request: Request, dept_in: DeptCreate):
    dept_service.create_dept(dept_in)
    return success(msg="部门创建成功")


@router.put("/{dept_id}", summary="更新部门")
@apply_rate_limit("30/minute")
def update_dept(request: Request, dept_id: int, dept_in: DeptUpdate):
    dept_service.update_dept(dept_id, dept_in)
    return success(msg="部门更新成功")


@router.get("/list", summary="获取部门列表")
@apply_rate_limit("60/minute")
def list_dept(request: Request, name: str = Query(None, description="部门名称")):
    dept_tree = dept_service.get_dept_tree(name or "")
    return success(data=dept_tree)


@router.get("/{dept_id}", summary="获取部门详情")
@apply_rate_limit("60/minute")
def get_dept(request: Request, dept_id: int):
    data = dept_service.get_dept_detail(dept_id)
    return success(data=data)


@router.delete("/{dept_id}", summary="删除部门")
@apply_rate_limit("30/minute")
def delete_dept(request: Request, dept_id: int):
    dept_service.delete_dept(dept_id)
    return success(msg="部门删除成功")