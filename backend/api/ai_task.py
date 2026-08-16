"""
AI 任务生成路由
提供调用大模型生成学习任务包、保存任务包、查询/删除任务包等接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.task_package import TaskPackage
from models.task_item import TaskItem
from schemas.common import ResponseOK
from schemas.task import AITaskRequest, TaskPackageCreate, TaskPackageOut
from utils.deps import get_current_user
from utils.ai_generator import generate_study_tasks

router = APIRouter(prefix="/api/ai-task", tags=["AI任务生成"])


@router.post("/generate", response_model=ResponseOK, summary="AI生成学习任务")
def generate_tasks(payload: AITaskRequest, current_user: User = Depends(get_current_user)):
    """调用 AI 大模型，根据学习目标生成结构化子任务列表"""
    tasks = generate_study_tasks(
        goal=payload.goal,
        daily_hours=payload.daily_hours,
        level=payload.level,
        category=payload.category,
        deadline_days=payload.deadline_days,
        learning_style=payload.learning_style,
        focus_points=payload.focus_points,
    )
    return ResponseOK(data=tasks)


@router.post("/save", response_model=ResponseOK, summary="保存AI生成的任务包")
def save_package(
    payload: TaskPackageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存 AI 生成的任务包及其子任务，publisher_id 关联当前用户"""
    package = TaskPackage(
        title=payload.title,
        category=payload.category,
        source=payload.source,
        publisher_id=current_user.id,
        description=payload.description,
        daily_hours=payload.daily_hours,
        level=payload.level,
        is_official=0,
        audit_status="pending",
    )
    db.add(package)
    db.flush()  # flush 以获取 package.id，便于关联子任务

    # 批量创建子任务
    for idx, item in enumerate(payload.items):
        task_item = TaskItem(
            package_id=package.id,
            name=item.name,
            description=item.description,
            sort_order=item.sort_order or idx,
            estimated_hours=item.estimated_hours,
        )
        db.add(task_item)

    db.commit()
    db.refresh(package)

    return ResponseOK(data=TaskPackageOut.model_validate(package).model_dump())


@router.get("/my-packages", response_model=ResponseOK, summary="获取我的任务包列表")
def my_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户创建的所有任务包列表"""
    packages = (
        db.query(TaskPackage)
        .filter(TaskPackage.publisher_id == current_user.id)
        .order_by(TaskPackage.created_at.desc())
        .all()
    )
    return ResponseOK(
        data=[TaskPackageOut.model_validate(p).model_dump() for p in packages]
    )


@router.get("/packages/{package_id}", response_model=ResponseOK, summary="获取任务包详情")
def get_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务包详情（含子任务列表）"""
    package = db.query(TaskPackage).filter(TaskPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="任务包不存在")

    return ResponseOK(data=TaskPackageOut.model_validate(package).model_dump())


@router.delete("/packages/{package_id}", response_model=ResponseOK, summary="删除任务包")
def delete_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除任务包（仅限创建者本人删除，级联删除子任务）"""
    package = db.query(TaskPackage).filter(TaskPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="任务包不存在")
    if package.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人的任务包")

    db.delete(package)  # cascade="all, delete-orphan" 会级联删除子任务
    db.commit()

    return ResponseOK(message="删除成功")
