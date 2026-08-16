"""通用响应模型"""
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    """统一响应基类"""
    code: int = 200
    message: str = "success"


class ResponseOK(ResponseBase):
    """简单成功响应"""
    data: Any | None = None


class PageResponse(ResponseBase, Generic[T]):
    """分页响应"""
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10


class TokenResponse(BaseModel):
    """登录令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict
