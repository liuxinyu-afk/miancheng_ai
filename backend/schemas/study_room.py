"""结伴自习相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class StudyRoomCreate(BaseModel):
    name: str = Field(..., max_length=100, description="房间名称")
    target_minutes: int = Field(default=120, ge=10, le=600, description="目标自习时长(分钟)")
    is_private: int = Field(default=0, description="0=公开 1=私密")
    max_members: int = Field(default=10, ge=2, le=50, description="最大成员数")
    # V7 新增
    tags: str = Field(default="", max_length=255, description="房间标签，逗号分隔")
    description: str = Field(default="", max_length=500, description="房间简介")
    category: str = Field(default="其他", max_length=50, description="房间分类")
    daily_target_minutes: int = Field(default=0, ge=0, le=960, description="每日目标时长(分钟)")


class StudyRoomOut(BaseModel):
    id: int
    name: str
    creator_id: int
    target_minutes: int
    is_private: int
    max_members: int
    status: str = "active"
    tags: str = ""
    description: str = ""
    announcement: str = ""
    category: str = "其他"
    daily_target_minutes: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyMinutesUpdate(BaseModel):
    """更新自习时长"""
    study_minutes: int = Field(..., ge=0, description="新增自习时长(分钟)")


class CheckinPayload(BaseModel):
    """结构化打卡表单"""
    completed: str = Field(default="", max_length=2000, description="今日完成")
    incomplete: str = Field(default="", max_length=2000, description="未完成")
    tomorrow_plan: str = Field(default="", max_length=2000, description="明日计划")
    mood: str = Field(default="", max_length=1000, description="心态碎碎念(选填)")
    study_minutes: int = Field(default=0, ge=0, description="本次学习时长(分钟)")


class AnnouncementPayload(BaseModel):
    """更新房间公告"""
    announcement: str = Field(..., max_length=2000, description="房间公告内容")
