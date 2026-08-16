"""私信路由 - 用户间一对一私信功能（仅限好友）"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from database import get_db
from models.user import User
from models.private_message import Conversation, PrivateMessage
from models.friendship import Friendship
from schemas.common import ResponseOK
from utils.deps import get_current_user

router = APIRouter(prefix="/api/message", tags=["私信"])


class SendMessageRequest(BaseModel):
    receiver_id: int = Field(..., description="接收者用户ID")
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")


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


def _get_or_create_conversation(db: Session, user1_id: int, user2_id: int) -> Conversation:
    """获取或创建两个用户之间的会话"""
    # 确保 user1_id < user2_id，保证唯一约束
    if user1_id > user2_id:
        user1_id, user2_id = user2_id, user1_id

    conv = db.query(Conversation).filter(
        Conversation.user1_id == user1_id,
        Conversation.user2_id == user2_id,
    ).first()

    if conv is None:
        conv = Conversation(user1_id=user1_id, user2_id=user2_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return conv


@router.get("/users", summary="搜索可发私信的用户")
def search_users(
    keyword: str = Query("", description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """搜索用户列表（排除自己），用于发起私信"""
    query = db.query(User).filter(User.id != current_user.id, User.status == 1)
    if keyword:
        query = query.filter(
            or_(
                User.nickname.contains(keyword),
                User.username.contains(keyword),
            )
        )
    users = query.limit(50).all()
    return ResponseOK(data=[
        {
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname or u.username,
            "role": u.role,
            "avatar": u.avatar if hasattr(u, 'avatar') else None,
        }
        for u in users
    ])


@router.post("/send", summary="发送私信")
def send_message(
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送私信给指定用户（非好友限3条）"""
    if payload.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能给自己发私信")

    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if receiver.status != 1:
        raise HTTPException(status_code=400, detail="该用户已被禁用")

    # 检查是否为好友
    is_friend = _are_friends(db, current_user.id, payload.receiver_id)

    # 非好友限制：最多发3条消息
    if not is_friend:
        sent_count = (
            db.query(PrivateMessage)
            .filter(
                PrivateMessage.sender_id == current_user.id,
                PrivateMessage.receiver_id == payload.receiver_id,
            )
            .count()
        )
        if sent_count >= 3:
            raise HTTPException(
                status_code=403,
                detail="你们还不是好友，非好友最多发送3条消息，请先添加好友"
            )

    # 获取或创建会话
    conv = _get_or_create_conversation(db, current_user.id, payload.receiver_id)

    # 创建消息
    msg = PrivateMessage(
        conversation_id=conv.id,
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        content=payload.content,
        is_read=0,
    )
    db.add(msg)

    # 更新会话最后消息
    conv.last_message = payload.content
    conv.last_message_at = msg.created_at

    db.commit()
    db.refresh(msg)

    return ResponseOK(data={
        "id": msg.id,
        "conversation_id": conv.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "is_read": msg.is_read,
        "created_at": msg.created_at,
        "is_friend": is_friend,
    })


@router.get("/conversations", summary="获取会话列表")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的所有会话列表"""
    convs = (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.user1_id == current_user.id,
                Conversation.user2_id == current_user.id,
            )
        )
        .order_by(
            Conversation.last_message_at.is_(None),
            Conversation.last_message_at.desc(),
        )
        .all()
    )

    result = []
    for conv in convs:
        # 对方用户
        other_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
        other = db.query(User).filter(User.id == other_id).first()
        if other is None:
            continue

        # 未读消息数
        unread_count = (
            db.query(PrivateMessage)
            .filter(
                PrivateMessage.conversation_id == conv.id,
                PrivateMessage.receiver_id == current_user.id,
                PrivateMessage.is_read == 0,
            )
            .count()
        )

        result.append({
            "id": conv.id,
            "other_user": {
                "id": other.id,
                "username": other.username,
                "nickname": other.nickname or other.username,
                "role": other.role,
                "avatar": other.avatar if hasattr(other, 'avatar') else None,
            },
            "last_message": conv.last_message or "",
            "last_message_at": conv.last_message_at,
            "unread_count": unread_count,
        })

    return ResponseOK(data=result)


@router.get("/conversation/{user_id}", summary="获取与某用户的消息记录")
def get_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取与指定用户的消息记录"""
    other = db.query(User).filter(User.id == user_id).first()
    if other is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 找到会话
    u1, u2 = min(current_user.id, user_id), max(current_user.id, user_id)
    conv = db.query(Conversation).filter(
        Conversation.user1_id == u1,
        Conversation.user2_id == u2,
    ).first()

    if conv is None:
        # 没有会话，返回空列表
        return ResponseOK(data={
            "conversation_id": None,
            "other_user": {
                "id": other.id,
                "username": other.username,
                "nickname": other.nickname or other.username,
                "role": other.role,
                "avatar": other.avatar if hasattr(other, 'avatar') else None,
            },
            "messages": [],
        })

    # 获取所有消息
    messages = (
        db.query(PrivateMessage)
        .filter(PrivateMessage.conversation_id == conv.id)
        .order_by(PrivateMessage.created_at.asc())
        .all()
    )

    # 标记接收方未读消息为已读
    for m in messages:
        if m.receiver_id == current_user.id and m.is_read == 0:
            m.is_read = 1
    db.commit()

    return ResponseOK(data={
        "conversation_id": conv.id,
        "other_user": {
            "id": other.id,
            "username": other.username,
            "nickname": other.nickname or other.username,
            "role": other.role,
            "avatar": other.avatar if hasattr(other, 'avatar') else None,
        },
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "is_read": m.is_read,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    })


@router.get("/unread-count", summary="获取未读私信总数")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的未读私信总数"""
    count = (
        db.query(PrivateMessage)
        .filter(
            PrivateMessage.receiver_id == current_user.id,
            PrivateMessage.is_read == 0,
        )
        .count()
    )
    return ResponseOK(data={"unread_count": count})
