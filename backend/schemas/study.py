"""学习打卡 & 笔记相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class CheckInRequest(BaseModel):
    """打卡请求"""
    task_id: int = Field(..., description="子任务ID")
    remark: str | None = Field(None, max_length=500, description="学习备注")


class CheckRecordOut(BaseModel):
    id: int
    user_id: int
    task_id: int
    status: str
    remark: str | None = None
    check_time: datetime

    model_config = {"from_attributes": True}


class NoteCreate(BaseModel):
    title: str | None = Field(None, max_length=200, description="笔记标题")
    content: str | None = Field(None, description="笔记内容")
    package_id: int | None = Field(None, description="关联任务包ID")
    is_public: int = Field(default=0, description="0=私有 1=公开")


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_public: int | None = None


class NoteOut(BaseModel):
    id: int
    user_id: int
    package_id: int | None = None
    title: str | None = None
    content: str | None = None
    is_public: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
