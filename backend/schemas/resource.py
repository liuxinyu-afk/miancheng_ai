"""资源集市相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    title: str = Field(..., max_length=100, description="资源标题")
    category: str = Field(default="其他", description="资源分类")
    content: str | None = Field(None, description="资源内容")
    attachment_url: str | None = Field(None, description="附件地址")


class ResourceOut(BaseModel):
    id: int
    title: str
    category: str
    content: str | None = None
    attachment_url: str | None = None
    publisher_id: int
    publisher_role: str
    is_teacher_certified: int = 0
    audit_status: str = "pending"
    reject_reason: str | None = None
    view_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
