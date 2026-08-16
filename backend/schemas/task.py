"""任务包 & 子任务相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class TaskItemOut(BaseModel):
    id: int | None = None
    name: str = Field(..., description="任务名称")
    description: str | None = Field(None, description="任务描述")
    sort_order: int = Field(default=0, description="排序")
    estimated_hours: float = Field(default=1.0, description="预计时长(小时)")

    model_config = {"from_attributes": True}


class TaskItemCreate(BaseModel):
    name: str
    description: str | None = None
    sort_order: int = 0
    estimated_hours: float = 1.0


class AITaskRequest(BaseModel):
    """AI 生成任务包请求"""
    goal: str = Field(..., min_length=2, max_length=200, description="学习目标")
    daily_hours: int = Field(..., ge=1, le=12, description="每日学习时长(小时)")
    level: str = Field(default="beginner", description="基础水平: beginner/intermediate/advanced")
    category: str | None = Field(None, description="学习领域分类")
    deadline_days: int | None = Field(None, description="目标完成天数")
    learning_style: str | None = Field(None, description="学习风格偏好: theory/practice/project/mixed")
    focus_points: str | None = Field(None, description="特别关注点/额外要求")


class TaskPackageCreate(BaseModel):
    """保存任务包请求（AI 生成后保存 或 手动创建）"""
    title: str = Field(..., max_length=100, description="任务标题")
    category: str = Field(default="其他", description="任务分类")
    description: str | None = Field(None, description="简介描述")
    daily_hours: int = Field(default=2, description="每日学习时长")
    level: str = Field(default="beginner", description="基础水平")
    source: str = Field(default="ai_generated", description="生成来源")
    items: list[TaskItemCreate] = Field(default_factory=list, description="子任务列表")


class TaskPackageOut(BaseModel):
    id: int
    title: str
    category: str
    source: str
    publisher_id: int | None = None
    description: str | None = None
    daily_hours: int = 2
    level: str = "beginner"
    is_official: int = 0
    audit_status: str = "pending"
    created_at: datetime
    items: list[TaskItemOut] = []

    model_config = {"from_attributes": True}
