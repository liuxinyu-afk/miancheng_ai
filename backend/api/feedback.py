"""
问题反馈路由
- 所有用户都可以提交问题反馈
- 管理员可以查看、回复、处理反馈
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.user import User
from models.feedback import Feedback
from schemas.common import ResponseOK, PageResponse
from utils.deps import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["问题反馈"])


# ==================== 请求体 Schema ====================

class FeedbackCreate(BaseModel):
    title: str
    content: str
    category: str = "其他"
    contact: Optional[str] = None


class FeedbackReply(BaseModel):
    reply: str
    status: str = "resolved"  # resolved / processing / closed


# ==================== 工具函数 ====================

CATEGORY_MAP = {
    "bug": "系统Bug",
    "suggestion": "功能建议",
    "account": "账号问题",
    "other": "其他问题",
}

STATUS_MAP = {
    "pending": "待处理",
    "processing": "处理中",
    "resolved": "已解决",
    "closed": "已关闭",
}


def _feedback_to_dict(fb: Feedback, db: Session, include_user: bool = False) -> dict:
    """将反馈对象转为字典"""
    result = {
        "id": fb.id,
        "user_id": fb.user_id,
        "title": fb.title,
        "content": fb.content,
        "category": fb.category,
        "category_label": CATEGORY_MAP.get(fb.category, fb.category),
        "contact": fb.contact,
        "status": fb.status,
        "status_label": STATUS_MAP.get(fb.status, fb.status),
        "reply": fb.reply,
        "reply_by": fb.reply_by,
        "replied_at": fb.replied_at,
        "created_at": fb.created_at,
    }
    if include_user:
        user = db.query(User).filter(User.id == fb.user_id).first()
        result["user_nickname"] = user.nickname if user else f"用户{fb.user_id}"
        result["user_username"] = user.username if user else ""
        result["user_role"] = user.role if user else ""
        if fb.reply_by:
            admin = db.query(User).filter(User.id == fb.reply_by).first()
            result["admin_name"] = admin.nickname if admin else f"用户{fb.reply_by}"
        else:
            result["admin_name"] = None
    return result


# ==================== 用户接口 ====================

@router.post("/create", response_model=ResponseOK, summary="提交问题反馈")
def create_feedback(
    fb: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """任何登录用户都可以提交问题反馈"""
    if not fb.title.strip() or not fb.content.strip():
        raise HTTPException(status_code=400, detail="标题和内容不能为空")

    db_fb = Feedback(
        user_id=current_user.id,
        title=fb.title.strip()[:200],
        content=fb.content.strip(),
        category=fb.category if fb.category in CATEGORY_MAP else "其他",
        contact=fb.contact.strip() if fb.contact else None,
        status="pending",
    )
    db.add(db_fb)
    db.commit()
    db.refresh(db_fb)
    return ResponseOK(data={"id": db_fb.id, "message": "反馈已提交，管理员将尽快处理"})


@router.get("/my", response_model=PageResponse, summary="获取我的反馈列表")
def my_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户提交的反馈列表"""
    query = db.query(Feedback).filter(Feedback.user_id == current_user.id)
    total = query.count()
    items = (
        query.order_by(Feedback.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [_feedback_to_dict(fb, db) for fb in items]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)


# ==================== 管理员接口 ====================

def _require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")


@router.get("/list", response_model=PageResponse, summary="获取反馈列表(管理员)")
def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None, description="按状态筛选"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """管理员查看所有反馈"""
    _require_admin(current_user)
    query = db.query(Feedback)
    if status:
        query = query.filter(Feedback.status == status)
    if category:
        query = query.filter(Feedback.category == category)
    total = query.count()
    items = (
        query.order_by(Feedback.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [_feedback_to_dict(fb, db, include_user=True) for fb in items]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)


@router.get("/stats", response_model=ResponseOK, summary="反馈统计(管理员)")
def feedback_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """管理员获取反馈统计数据"""
    _require_admin(current_user)
    total = db.query(Feedback).count()
    pending = db.query(Feedback).filter(Feedback.status == "pending").count()
    processing = db.query(Feedback).filter(Feedback.status == "processing").count()
    resolved = db.query(Feedback).filter(Feedback.status == "resolved").count()
    closed = db.query(Feedback).filter(Feedback.status == "closed").count()
    return ResponseOK(data={
        "total": total,
        "pending": pending,
        "processing": processing,
        "resolved": resolved,
        "closed": closed,
    })


@router.put("/{fb_id}/reply", response_model=ResponseOK, summary="回复反馈(管理员)")
def reply_feedback(
    fb_id: int,
    body: FeedbackReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """管理员回复反馈并更新状态"""
    _require_admin(current_user)
    fb = db.query(Feedback).filter(Feedback.id == fb_id).first()
    if fb is None:
        raise HTTPException(status_code=404, detail="反馈不存在")

    fb.reply = body.reply.strip()
    fb.reply_by = current_user.id
    fb.replied_at = datetime.now()
    fb.status = body.status if body.status in STATUS_MAP else "resolved"
    db.commit()
    db.refresh(fb)
    return ResponseOK(data=_feedback_to_dict(fb, db, include_user=True))


@router.put("/{fb_id}/status", response_model=ResponseOK, summary="更新反馈状态(管理员)")
def update_status(
    fb_id: int,
    status: str = Query(..., description="新状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """管理员更新反馈状态（不回复，仅改状态）"""
    _require_admin(current_user)
    fb = db.query(Feedback).filter(Feedback.id == fb_id).first()
    if fb is None:
        raise HTTPException(status_code=404, detail="反馈不存在")
    if status not in STATUS_MAP:
        raise HTTPException(status_code=400, detail="无效状态")
    fb.status = status
    db.commit()
    db.refresh(fb)
    return ResponseOK(data=_feedback_to_dict(fb, db, include_user=True))
