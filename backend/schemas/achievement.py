"""成果帖子 & 评论相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, description="图文内容")
    images: list[str] | None = Field(None, description="图片URL列表")
    tags: str = Field(default="", max_length=255, description="内容标签，逗号分隔")
    is_anonymous: int = Field(default=0, description="0=实名 1=匿名")


class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    images: list[str] | None = None
    like_count: int = 0
    comment_count: int = 0
    audit_status: str = "pending"
    created_at: datetime
    author_name: str | None = None
    author_role: str | None = None
    author_avatar: str | None = None
    tags: str = ""
    is_anonymous: int = 0
    reject_reason: str | None = None

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: int | None = Field(None, description="父评论ID（回复某条评论）")


class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    is_teacher: int = 0
    parent_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
