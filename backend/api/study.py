"""
学习中心路由 - 打卡、笔记、学习进度
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.task_item import TaskItem
from models.check_record import CheckRecord
from models.note import Note
from schemas.common import ResponseOK, PageResponse
from schemas.study import (
    CheckInRequest,
    CheckRecordOut,
    NoteCreate,
    NoteUpdate,
    NoteOut,
)
from utils.deps import get_current_user

router = APIRouter(prefix="/api/study", tags=["学习中心"])


# ==================== 打卡相关 ====================

@router.post("/checkin", response_model=ResponseOK)
def checkin(
    payload: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """打卡：对指定子任务创建完成记录"""
    # 校验子任务是否存在
    task = db.query(TaskItem).filter(TaskItem.id == payload.task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="子任务不存在")

    record = CheckRecord(
        user_id=current_user.id,
        task_id=payload.task_id,
        status="completed",
        remark=payload.remark,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ResponseOK(data=CheckRecordOut.model_validate(record).model_dump())


@router.get("/checkin/today", response_model=ResponseOK)
def get_today_checkin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取今日打卡记录"""
    today = date.today()
    # 构造今天的起止时间范围，避免对列使用函数导致索引失效
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    records = (
        db.query(CheckRecord)
        .filter(
            CheckRecord.user_id == current_user.id,
            CheckRecord.check_time >= start,
            CheckRecord.check_time < end,
        )
        .order_by(CheckRecord.check_time.desc())
        .all()
    )
    return ResponseOK(
        data=[CheckRecordOut.model_validate(r).model_dump() for r in records]
    )


@router.get("/checkin/history", response_model=PageResponse[CheckRecordOut])
def get_checkin_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取打卡历史(分页)"""
    query = db.query(CheckRecord).filter(CheckRecord.user_id == current_user.id)
    total = query.count()
    records = (
        query.order_by(CheckRecord.check_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse[CheckRecordOut](
        data=[CheckRecordOut.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
    )


# ==================== 笔记相关 ====================

@router.post("/notes", response_model=ResponseOK)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建学习笔记"""
    note = Note(
        user_id=current_user.id,
        package_id=payload.package_id,
        title=payload.title,
        content=payload.content,
        is_public=payload.is_public,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return ResponseOK(data=NoteOut.model_validate(note).model_dump())


@router.get("/notes", response_model=ResponseOK)
def get_my_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我的笔记列表"""
    notes = (
        db.query(Note)
        .filter(Note.user_id == current_user.id)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return ResponseOK(
        data=[NoteOut.model_validate(n).model_dump() for n in notes]
    )


@router.put("/notes/{note_id}", response_model=ResponseOK)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新笔记(只能修改自己的笔记)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人的笔记")

    # 仅更新实际传入的字段
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return ResponseOK(data=NoteOut.model_validate(note).model_dump())


@router.delete("/notes/{note_id}", response_model=ResponseOK)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除笔记(只能删除自己的笔记)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人的笔记")

    db.delete(note)
    db.commit()
    return ResponseOK(message="删除成功")


# ==================== 学习进度 ====================

@router.get("/progress/{package_id}", response_model=ResponseOK)
def get_study_progress(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取某任务包的学习进度(已打卡子任务数/总子任务数)"""
    # 该任务包下的子任务总数
    total = (
        db.query(TaskItem).filter(TaskItem.package_id == package_id).count()
    )
    if total == 0:
        return ResponseOK(
            data={"total": 0, "completed": 0, "progress": 0.0}
        )

    # 当前用户在该任务包下已完成的子任务数(按 task_id 去重)
    completed = (
        db.query(CheckRecord.task_id)
        .join(TaskItem, TaskItem.id == CheckRecord.task_id)
        .filter(
            CheckRecord.user_id == current_user.id,
            TaskItem.package_id == package_id,
            CheckRecord.status == "completed",
        )
        .distinct()
        .count()
    )

    return ResponseOK(
        data={
            "total": total,
            "completed": completed,
            "progress": round(completed / total, 4),
        }
    )
