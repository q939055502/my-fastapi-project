from pydantic import BaseModel, Field


class ResourceBase(BaseModel):
    code: str = Field(..., description="资源编码", example="user:list")
    name: str = Field(..., description="资源名称", example="用户列表")
    type: int = Field(..., description="资源类型：1-菜单 2-API 3-按钮", example=1)
    api_path: str | None = Field(None, description="API路径", example="/api/v1/users/list")
    api_method: str | None = Field(None, description="请求方法", example="GET")
    path: str | None = Field(None, description="前端路由路径", example="/users")
    icon: str | None = Field(None, description="图标", example="user")
    parent_id: int | None = Field(None, description="父资源ID")
    sort: int = Field(0, description="排序")
    remark: str | None = Field("", description="描述")
    status: int = Field(1, description="状态：1-启用 0-禁用")


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    code: str | None = Field(None, description="资源编码")
    name: str | None = Field(None, description="资源名称")
    type: int | None = Field(None, description="资源类型")
    api_path: str | None = Field(None, description="API路径")
    api_method: str | None = Field(None, description="请求方法")
    path: str | None = Field(None, description="前端路由路径")
    icon: str | None = Field(None, description="图标")
    parent_id: int | None = Field(None, description="父资源ID")
    sort: int | None = Field(None, description="排序")
    remark: str | None = Field(None, description="描述")
    status: int | None = Field(None, description="状态")
