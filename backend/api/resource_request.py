"""
交流广场路由
- 用户发布帖子（可发图片）
- 其他用户可以回复（可发图片）
- 发帖者可以采纳回复
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.user import User
from models.resource_request import ResourceRequest, ResourceReply
from schemas.common import ResponseOK
from utils.deps import get_current_user

router = APIRouter(prefix="/api/resource-plaza", tags=["交流广场"])

# 图片上传目录
PLAZA_IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "plaza")


# ==================== 请求体 Schema ====================

class RequestCreate(BaseModel):
    title: str
    content: str
    category: str = "其他"
    tags: str = ""
    images: str = ""  # 逗号分隔的图片URL


class ReplyCreate(BaseModel):
    content: str
    resource_link: str = ""
    resource_type: str = "link"
    images: str = ""  # 逗号分隔的图片URL


# ==================== 工具函数 ====================

def _parse_images(images_str):
    """把逗号分隔的图片字符串转为列表"""
    if not images_str:
        return []
    return [img.strip() for img in images_str.split(",") if img.strip()]


def _request_to_dict(req, db, current_user_id=None):
    """将帖子对象转为字典"""
    user = db.query(User).filter(User.id == req.user_id).first()
    return {
        "id": req.id,
        "user_id": req.user_id,
        "title": req.title,
        "content": req.content,
        "category": req.category,
        "tags": req.tags or "",
        "images": _parse_images(getattr(req, 'images', '')),
        "reply_count": req.reply_count,
        "view_count": req.view_count,
        "status": req.status,
        "created_at": req.created_at,
        "updated_at": req.updated_at,
        "author_name": user.nickname if user else f"用户{req.user_id}",
        "author_avatar": user.avatar if user else None,
        "author_role": user.role if user else None,
        "is_owner": current_user_id == req.user_id if current_user_id else False,
    }


def _reply_to_dict(reply, db, current_user_id=None):
    """将回复对象转为字典"""
    user = db.query(User).filter(User.id == reply.user_id).first()
    return {
        "id": reply.id,
        "request_id": reply.request_id,
        "user_id": reply.user_id,
        "content": reply.content,
        "resource_link": reply.resource_link or "",
        "images": _parse_images(getattr(reply, 'images', '')),
        "resource_type": reply.resource_type,
        "is_accepted": reply.is_accepted,
        "created_at": reply.created_at,
        "author_name": user.nickname if user else f"用户{reply.user_id}",
        "author_avatar": user.avatar if user else None,
        "author_role": user.role if user else None,
        "is_owner": current_user_id == reply.user_id if current_user_id else False,
    }


# ==================== 图片上传接口 ====================

@router.post("/upload-image", response_model=ResponseOK)
async def upload_plaza_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传交流广场图片"""
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/jpg"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WEBP 格式")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

    os.makedirs(PLAZA_IMG_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "img.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(PLAZA_IMG_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    return ResponseOK(message="上传成功", data={"url": f"/uploads/plaza/{filename}"})


# ==================== 帖子接口 ====================

@router.get("/list", response_model=ResponseOK)
def list_requests(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取帖子列表（所有用户可见）"""
    q = db.query(ResourceRequest)

    if keyword:
        q = q.filter(
            ResourceRequest.title.contains(keyword) |
            ResourceRequest.content.contains(keyword)
        )
    if category and category != "全部":
        q = q.filter(ResourceRequest.category == category)
    if status:
        q = q.filter(ResourceRequest.status == status)

    total = q.count()
    items = (
        q.order_by(ResourceRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ResponseOK(data={
        "total": total,
        "list": [_request_to_dict(r, db, current_user.id) for r in items],
    })


@router.post("/create", response_model=ResponseOK)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发布帖子"""
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="请输入标题")
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="请输入内容")

    req = ResourceRequest(
        user_id=current_user.id,
        title=payload.title.strip(),
        content=payload.content.strip(),
        category=payload.category or "其他",
        tags=payload.tags or "",
        images=payload.images or "",
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return ResponseOK(message="发布成功", data=_request_to_dict(req, db, current_user.id))


@router.get("/{request_id}", response_model=ResponseOK)
def get_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取帖子详情"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 浏览量+1
    req.view_count = (req.view_count or 0) + 1
    db.commit()

    return ResponseOK(data=_request_to_dict(req, db, current_user.id))


@router.put("/{request_id}/status", response_model=ResponseOK)
def update_request_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新帖子状态（仅发布者可操作）"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if req.user_id != current_user.id and current_user.role not in ("admin", "auditor"):
        raise HTTPException(status_code=403, detail="仅发布者可操作")

    if status not in ("open", "solved", "closed"):
        raise HTTPException(status_code=400, detail="无效状态")

    req.status = status
    db.commit()
    return ResponseOK(message="状态已更新")


@router.delete("/{request_id}", response_model=ResponseOK)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除帖子（仅发布者/管理员可操作）"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if req.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除")

    # 先删回复
    db.query(ResourceReply).filter(ResourceReply.request_id == request_id).delete()
    db.delete(req)
    db.commit()
    return ResponseOK(message="已删除")


# ==================== 回复接口 ====================

@router.get("/{request_id}/replies", response_model=ResponseOK)
def list_replies(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取帖子的所有回复"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")

    replies = (
        db.query(ResourceReply)
        .filter(ResourceReply.request_id == request_id)
        .order_by(
            ResourceReply.is_accepted.desc(),
            ResourceReply.created_at.asc(),
        )
        .all()
    )

    return ResponseOK(data=[_reply_to_dict(r, db, current_user.id) for r in replies])


@router.post("/{request_id}/replies", response_model=ResponseOK)
def create_reply(
    request_id: int,
    payload: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """回复帖子（可附带图片）"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if req.status == "closed":
        raise HTTPException(status_code=400, detail="该帖子已关闭，无法回复")
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="请输入回复内容")

    reply = ResourceReply(
        request_id=request_id,
        user_id=current_user.id,
        content=payload.content.strip(),
        resource_link=payload.resource_link or "",
        images=payload.images or "",
        resource_type=payload.resource_type or "link",
    )
    db.add(reply)

    req.reply_count = (req.reply_count or 0) + 1
    db.commit()
    db.refresh(reply)

    return ResponseOK(message="回复成功", data=_reply_to_dict(reply, db, current_user.id))


@router.put("/{request_id}/replies/{reply_id}/accept", response_model=ResponseOK)
def accept_reply(
    request_id: int,
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """采纳回复（仅帖子发布者可操作）"""
    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if req.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅发布者可采纳回复")

    reply = db.query(ResourceReply).filter(
        ResourceReply.id == reply_id,
        ResourceReply.request_id == request_id,
    ).first()
    if reply is None:
        raise HTTPException(status_code=404, detail="回复不存在")

    db.query(ResourceReply).filter(
        ResourceReply.request_id == request_id,
        ResourceReply.is_accepted == 1,
    ).update({ResourceReply.is_accepted: 0})

    reply.is_accepted = 1
    req.status = "solved"
    db.commit()

    return ResponseOK(message="已采纳该回复")


@router.delete("/{request_id}/replies/{reply_id}", response_model=ResponseOK)
def delete_reply(
    request_id: int,
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除回复（仅回复者本人/管理员可操作）"""
    reply = db.query(ResourceReply).filter(
        ResourceReply.id == reply_id,
        ResourceReply.request_id == request_id,
    ).first()
    if reply is None:
        raise HTTPException(status_code=404, detail="回复不存在")
    if reply.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除")

    req = db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()
    if req:
        req.reply_count = max(0, (req.reply_count or 0) - 1)

    db.delete(reply)
    db.commit()
    return ResponseOK(message="已删除回复")


# ==================== 我的帖子 ====================

@router.get("/my/requests", response_model=ResponseOK)
def my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我发布的帖子"""
    items = (
        db.query(ResourceRequest)
        .filter(ResourceRequest.user_id == current_user.id)
        .order_by(ResourceRequest.created_at.desc())
        .all()
    )
    return ResponseOK(data=[_request_to_dict(r, db, current_user.id) for r in items])
