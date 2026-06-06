from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfileOut(BaseModel):
    """个人信息响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    alias: str | None = Field(None, description="姓名/昵称")
    avatar: str | None = Field(None, description="头像URL")
    gender: int = Field(0, description="性别：0=未知，1=男，2=女")
    last_login: datetime | None = Field(None, description="最后登录时间")
    last_login_ip: str | None = Field(None, description="最后登录IP")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    remark: str | None = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)


class UpdateMyProfileIn(BaseModel):
    """更新个人信息请求"""
    alias: str | None = Field(None, description="姓名/昵称", max_length=30)
    avatar: str | None = Field(None, description="头像URL", max_length=500)
    gender: int | None = Field(None, description="性别：0=未知，1=男，2=女")
    remark: str | None = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)
