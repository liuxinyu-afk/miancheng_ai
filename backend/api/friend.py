"""好友路由 - 搜索加好友、同意/拒绝、好友列表"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from database import get_db
from models.user import User
from models.friendship import Friendship
from models.misc import Message
from schemas.common import ResponseOK
from utils.deps import get_current_user

router = APIRouter(prefix="/api/friend", tags=["好友"])


class FriendRequestPayload(BaseModel):
    receiver_id: int = Field(..., description="被添加的用户ID")


def _user_brief(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "nickname": u.nickname or u.username,
        "role": u.role,
        "avatar": u.avatar if hasattr(u, "avatar") else None,
    }


def _are_friends(db: Session, uid1: int, uid2: int) -> bool:
    """检查两人是否已经是好友"""
    return (
        db.query(Friendship)
        .filter(
            or_(
                and_(Friendship.requester_id == uid1, Friendship.receiver_id == uid2),
                and_(Friendship.requester_id == uid2, Friendship.receiver_id == uid1),
            ),
            Friendship.status == "accepted",
        )
        .first()
        is not None
    )


def _pending_request_exists(db: Session, uid1: int, uid2: int) -> bool:
    """检查是否已有待处理的好友请求"""
    return (
        db.query(Friendship)
        .filter(
            or_(
                and_(Friendship.requester_id == uid1, Friendship.receiver_id == uid2),
                and_(Friendship.requester_id == uid2, Friendship.receiver_id == uid1),
            ),
            Friendship.status == "pending",
        )
        .first()
        is not None
    )


# ==================== 搜索用户 ====================

@router.get("/search", summary="搜索用户加好友")
def search_users(
    keyword: str = Query("", description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """搜索用户，返回好友状态信息"""
    query = db.query(User).filter(User.id != current_user.id, User.status == 1)
    if keyword:
        query = query.filter(
            or_(
                User.nickname.contains(keyword),
                User.username.contains(keyword),
            )
        )
    users = query.limit(50).all()

    result = []
    for u in users:
        # 检查好友状态
        friendship = (
            db.query(Friendship)
            .filter(
                or_(
                    and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == u.id),
                    and_(Friendship.requester_id == u.id, Friendship.receiver_id == current_user.id),
                )
            )
            .first()
        )

        if friendship is None:
            friend_status = "none"
        elif friendship.status == "accepted":
            friend_status = "friend"
        elif friendship.status == "pending":
            if friendship.requester_id == current_user.id:
                friend_status = "pending_sent"  # 我发出的请求待处理
            else:
                friend_status = "pending_received"  # 对方发给我的请求待处理
        else:
            friend_status = "none"

        result.append({
            **_user_brief(u),
            "friend_status": friend_status,
        })

    return ResponseOK(data=result)


# ==================== 发送好友请求 ====================

@router.post("/request", summary="发送好友请求")
def send_friend_request(
    payload: FriendRequestPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """向指定用户发送好友请求"""
    if payload.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if receiver.status != 1:
        raise HTTPException(status_code=400, detail="该用户已被禁用")

    # 检查是否已经是好友
    if _are_friends(db, current_user.id, payload.receiver_id):
        raise HTTPException(status_code=400, detail="你们已经是好友了")

    # 检查是否已有待处理请求
    if _pending_request_exists(db, current_user.id, payload.receiver_id):
        raise HTTPException(status_code=400, detail="已存在待处理的好友请求")

    # 检查对方是否曾拒绝过
    existing = (
        db.query(Friendship)
        .filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == payload.receiver_id),
                and_(Friendship.requester_id == payload.receiver_id, Friendship.receiver_id == current_user.id),
            ),
        )
        .first()
    )

    if existing and existing.status == "rejected":
        # 重新发起请求
        existing.status = "pending"
        existing.requester_id = current_user.id
        existing.receiver_id = payload.receiver_id
        db.commit()
        db.refresh(existing)
        friendship_id = existing.id
    else:
        # 创建新请求
        friendship = Friendship(
            requester_id=current_user.id,
            receiver_id=payload.receiver_id,
            status="pending",
        )
        db.add(friendship)
        db.commit()
        db.refresh(friendship)
        friendship_id = friendship.id

    # 给接收者发通知
    notice = Message(
        user_id=payload.receiver_id,
        title="收到好友请求",
        content=f"{current_user.nickname or current_user.username} 想添加你为好友",
        msg_type="friend_request",
        is_read=0,
        sender_id=current_user.id,
        related_id=friendship_id,
    )
    db.add(notice)
    db.commit()

    return ResponseOK(data={"friendship_id": friendship_id, "status": "pending"})


# ==================== 好友请求列表（我收到的） ====================

@router.get("/requests", summary="收到的好友请求列表")
def get_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我收到的好友请求（待处理）"""
    friendships = (
        db.query(Friendship)
        .filter(
            Friendship.receiver_id == current_user.id,
            Friendship.status == "pending",
        )
        .order_by(Friendship.created_at.desc())
        .all()
    )

    result = []
    for f in friendships:
        requester = db.query(User).filter(User.id == f.requester_id).first()
        if requester is None:
            continue
        result.append({
            "id": f.id,
            "user": _user_brief(requester),
            "created_at": f.created_at,
        })

    return ResponseOK(data=result)


# ==================== 同意好友请求 ====================

@router.post("/{friendship_id}/accept", summary="同意好友请求")
def accept_friend_request(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同意好友请求"""
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if friendship is None:
        raise HTTPException(status_code=404, detail="好友请求不存在")

    if friendship.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此好友请求")

    if friendship.status != "pending":
        raise HTTPException(status_code=400, detail="该请求已处理")

    friendship.status = "accepted"
    db.commit()

    # 给请求者发通知
    requester = db.query(User).filter(User.id == friendship.requester_id).first()
    notice = Message(
        user_id=friendship.requester_id,
        title="好友请求已通过",
        content=f"{current_user.nickname or current_user.username} 同意了你的好友请求，现在可以开始私信了",
        msg_type="friend_accept",
        is_read=0,
        sender_id=current_user.id,
        related_id=friendship.id,
    )
    db.add(notice)
    db.commit()

    return ResponseOK(data={"status": "accepted"})


# ==================== 拒绝好友请求 ====================

@router.post("/{friendship_id}/reject", summary="拒绝好友请求")
def reject_friend_request(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """拒绝好友请求"""
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if friendship is None:
        raise HTTPException(status_code=404, detail="好友请求不存在")

    if friendship.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此好友请求")

    if friendship.status != "pending":
        raise HTTPException(status_code=400, detail="该请求已处理")

    friendship.status = "rejected"
    db.commit()

    return ResponseOK(data={"status": "rejected"})


# ==================== 好友列表 ====================

@router.get("/list", summary="获取好友列表")
def get_friends_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的好友列表"""
    friendships = (
        db.query(Friendship)
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.receiver_id == current_user.id,
            ),
            Friendship.status == "accepted",
        )
        .order_by(Friendship.updated_at.desc())
        .all()
    )

    result = []
    for f in friendships:
        friend_id = f.receiver_id if f.requester_id == current_user.id else f.requester_id
        friend = db.query(User).filter(User.id == friend_id).first()
        if friend is None:
            continue
        result.append(_user_brief(friend))

    return ResponseOK(data=result)


# ==================== 检查好友状态 ====================

@router.get("/status/{user_id}", summary="检查与某用户的好友状态")
def get_friend_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查当前用户与目标用户的好友关系状态"""
    if user_id == current_user.id:
        return ResponseOK(data={"status": "self"})

    friendship = (
        db.query(Friendship)
        .filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == user_id),
                and_(Friendship.requester_id == user_id, Friendship.receiver_id == current_user.id),
            ),
        )
        .first()
    )

    if friendship is None:
        status = "none"
    elif friendship.status == "accepted":
        status = "friend"
    elif friendship.status == "pending":
        if friendship.requester_id == current_user.id:
            status = "pending_sent"
        else:
            status = "pending_received"
    else:
        status = "none"

    return ResponseOK(data={"status": status})


# ==================== 删除好友 ====================

@router.delete("/{user_id}", summary="删除好友")
def remove_friend(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除好友关系"""
    friendship = (
        db.query(Friendship)
        .filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == user_id),
                and_(Friendship.requester_id == user_id, Friendship.receiver_id == current_user.id),
            ),
            Friendship.status == "accepted",
        )
        .first()
    )

    if friendship is None:
        raise HTTPException(status_code=404, detail="好友关系不存在")

    db.delete(friendship)
    db.commit()

    return ResponseOK(data={"status": "removed"})
