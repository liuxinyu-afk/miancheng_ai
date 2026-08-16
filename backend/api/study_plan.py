"""
学习计划路由（学生专属）
学生可以创建学习计划、跟踪进度
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.study_plan import StudyPlan
from schemas.common import ResponseOK, PageResponse
from utils.deps import get_current_user, require_roles

router = APIRouter(
    prefix="/api/study-plan",
    tags=["学习计划"],
    dependencies=[Depends(require_roles("student", "admin"))],
)


class PlanCreate(BaseModel):
    title: str = Field(..., max_length=100, description="计划标题")
    subject: str = Field(default="", max_length=50, description="学科")
    daily_goal_minutes: int = Field(default=120, ge=10, le=960, description="每日目标时长")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")


class PlanUpdate(BaseModel):
    title: str | None = None
    subject: str | None = None
    daily_goal_minutes: int | None = Field(None, ge=10, le=960)
    status: str | None = Field(None, description="active/completed/abandoned")
    progress: int | None = Field(None, ge=0, le=100)


def _plan_to_dict(plan: StudyPlan) -> dict:
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "title": plan.title,
        "subject": plan.subject,
        "daily_goal_minutes": plan.daily_goal_minutes,
        "start_date": plan.start_date.isoformat() if plan.start_date else "",
        "end_date": plan.end_date.isoformat() if plan.end_date else "",
        "status": plan.status,
        "progress": plan.progress,
        "created_at": plan.created_at,
    }


@router.post("/", response_model=ResponseOK, summary="创建学习计划")
def create_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = date.fromisoformat(payload.start_date)
    end = date.fromisoformat(payload.end_date)
    if end <= start:
        raise HTTPException(status_code=400, detail="结束日期必须晚于开始日期")

    plan = StudyPlan(
        user_id=current_user.id,
        title=payload.title,
        subject=payload.subject,
        daily_goal_minutes=payload.daily_goal_minutes,
        start_date=start,
        end_date=end,
        status="active",
        progress=0,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return ResponseOK(data=_plan_to_dict(plan))


@router.get("/", response_model=ResponseOK, summary="获取我的学习计划")
def get_my_plans(
    status: str = Query("", description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id)
    if status:
        query = query.filter(StudyPlan.status == status)
    plans = query.order_by(StudyPlan.created_at.desc()).all()
    return ResponseOK(data=[_plan_to_dict(p) for p in plans])


@router.put("/{plan_id}", response_model=ResponseOK, summary="更新学习计划")
def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="学习计划不存在")

    if payload.title is not None:
        plan.title = payload.title
    if payload.subject is not None:
        plan.subject = payload.subject
    if payload.daily_goal_minutes is not None:
        plan.daily_goal_minutes = payload.daily_goal_minutes
    if payload.status is not None:
        plan.status = payload.status
    if payload.progress is not None:
        plan.progress = payload.progress

    db.commit()
    db.refresh(plan)
    return ResponseOK(data=_plan_to_dict(plan))


@router.delete("/{plan_id}", response_model=ResponseOK, summary="删除学习计划")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="学习计划不存在")
    db.delete(plan)
    db.commit()
    return ResponseOK(message="删除成功")
