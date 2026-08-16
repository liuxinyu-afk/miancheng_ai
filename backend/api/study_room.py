"""
结伴自习路由 - 自习房间管理 + 群聊功能 + 结构化打卡 + 分区
自习房间/打卡群 类似微信群，成员可以相互交流沟通。
管理员/审核员进入即拥有群管理权限。
V7: 新增标签/分类/简介/公告、自习区&闲聊区分区、结构化打卡
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func as sa_func, cast, Date
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

from database import get_db
from models.user import User
from models.study_room import StudyRoom, StudyRoomMember, StudyRoomCheckin
from models.study_room_message import StudyRoomMessage
from schemas.common import ResponseOK, PageResponse
from schemas.study_room import (
    StudyRoomCreate,
    StudyRoomOut,
    StudyMinutesUpdate,
    CheckinPayload,
    AnnouncementPayload,
)
from utils.deps import get_current_user

router = APIRouter(prefix="/api/study-room", tags=["结伴自习"])


class SendMessagePayload(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")
    zone: str = Field(default="chat", description="消息分区: chat=闲聊 study=自习")


def _reset_daily_if_needed(member: StudyRoomMember):
    """如果跨天了，重置今日学习时长"""
    today = date.today()
    if member.last_study_date is None or member.last_study_date != today:
        member.today_minutes = 0
        member.last_study_date = today


def _room_to_dict(room: StudyRoom, db: Session, current_user_id: int | None = None, current_role: str | None = None) -> dict:
    """将 StudyRoom 对象转为包含额外字段的字典"""
    creator = db.query(User).filter(User.id == room.creator_id).first()
    owner_name = creator.nickname or creator.username if creator else f"用户{room.creator_id}"

    member_count = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room.id,
            StudyRoomMember.status == "active",
        )
        .count()
    )

    # 在线自习人数
    studying_count = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room.id,
            StudyRoomMember.is_studying == 1,
            StudyRoomMember.status == "active",
        )
        .count()
    )

    is_member = False
    member_status = None
    if current_user_id:
        existing = (
            db.query(StudyRoomMember)
            .filter(
                StudyRoomMember.room_id == room.id,
                StudyRoomMember.user_id == current_user_id,
            )
            .first()
        )
        is_member = existing is not None and existing.status == "active"
        member_status = existing.status if existing else None

    can_manage = current_role in ("admin", "auditor") if current_role else False

    # 最近一条闲聊消息
    last_msg = (
        db.query(StudyRoomMessage)
        .filter(
            StudyRoomMessage.room_id == room.id,
            StudyRoomMessage.zone == "chat",
        )
        .order_by(StudyRoomMessage.created_at.desc())
        .first()
    )

    # 今日总学习时长
    today = date.today()
    today_total = (
        db.query(sa_func.sum(StudyRoomMember.today_minutes))
        .filter(
            StudyRoomMember.room_id == room.id,
            StudyRoomMember.last_study_date == today,
        )
        .scalar()
    ) or 0

    return {
        "id": room.id,
        "name": room.name,
        "creator_id": room.creator_id,
        "target_minutes": room.target_minutes,
        "is_private": room.is_private,
        "max_members": room.max_members,
        "status": room.status,
        "created_at": room.created_at,
        "owner_name": owner_name,
        "owner_avatar": creator.avatar if creator else None,
        "owner_role": creator.role if creator else None,
        "current_members": member_count,
        "studying_count": studying_count,
        "is_member": is_member,
        "member_status": member_status,
        "can_manage": can_manage,
        "last_message": last_msg.content[:100] if last_msg else "",
        "last_message_at": last_msg.created_at if last_msg else None,
        # V7 新增字段
        "tags": room.tags or "",
        "description": room.description or "",
        "announcement": room.announcement or "",
        "category": room.category or "其他",
        "daily_target_minutes": room.daily_target_minutes or 0,
        "today_total_minutes": today_total,
        # V8 新增：待审核人数（仅管理员/群主可见）
        "pending_count": (
            db.query(StudyRoomMember)
            .filter(
                StudyRoomMember.room_id == room.id,
                StudyRoomMember.status == "pending",
            )
            .count()
            if can_manage or (current_user_id and room.creator_id == current_user_id)
            else 0
        ),
    }


# ==================== 房间 CRUD ====================

@router.post("/create", response_model=ResponseOK)
def create_room(
    payload: StudyRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建自习房间（类似创建微信群），创建者自动成为群主"""
    room = StudyRoom(
        name=payload.name,
        creator_id=current_user.id,
        target_minutes=payload.target_minutes,
        is_private=payload.is_private,
        max_members=payload.max_members,
        status="active",
        tags=payload.tags,
        description=payload.description,
        category=payload.category,
        daily_target_minutes=payload.daily_target_minutes,
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # 创建者自动加入房间
    member = StudyRoomMember(
        room_id=room.id,
        user_id=current_user.id,
        study_minutes=0,
        is_studying=0,
        today_minutes=0,
        last_study_date=date.today(),
    )
    db.add(member)
    db.commit()

    return ResponseOK(data=_room_to_dict(room, db, current_user.id, current_user.role))


@router.get("/list", response_model=PageResponse)
def get_room_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    keyword: str = Query("", description="搜索关键词"),
    category: str = Query("", description="分类筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取自习房间列表"""
    query = db.query(StudyRoom).filter(StudyRoom.status == "active")

    if current_user.role not in ("admin", "auditor"):
        my_room_ids = (
            db.query(StudyRoomMember.room_id)
            .filter(
                StudyRoomMember.user_id == current_user.id,
                StudyRoomMember.status == "active",
            )
            .subquery()
        )
        query = query.filter(
            or_(
                StudyRoom.is_private == 0,
                StudyRoom.id.in_(my_room_ids),
            )
        )

    if keyword:
        query = query.filter(
            or_(
                StudyRoom.name.contains(keyword),
                StudyRoom.description.contains(keyword),
                StudyRoom.tags.contains(keyword),
            )
        )
    if category and category != "全部":
        query = query.filter(StudyRoom.category == category)

    total = query.count()
    rooms = (
        query.order_by(StudyRoom.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [_room_to_dict(r, db, current_user.id, current_user.role) for r in rooms]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)


@router.get("/my-rooms", response_model=ResponseOK)
def get_my_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我加入的自习房间"""
    rooms = (
        db.query(StudyRoom)
        .join(StudyRoomMember, StudyRoomMember.room_id == StudyRoom.id)
        .filter(
            StudyRoomMember.user_id == current_user.id,
            StudyRoomMember.status == "active",
        )
        .order_by(StudyRoom.created_at.desc())
        .all()
    )
    return ResponseOK(
        data=[_room_to_dict(r, db, current_user.id, current_user.role) for r in rooms]
    )


# ==================== 房间统计 ====================

@router.get("/{room_id}/stats", response_model=ResponseOK)
def get_room_stats(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取房间统计信息：今日总学习时长、在线人数、打卡人数"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    today = date.today()
    members = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.status == "active",
        )
        .all()
    )

    # 重置跨天数据
    for m in members:
        _reset_daily_if_needed(m)
    db.commit()

    studying_count = sum(1 for m in members if m.is_studying == 1)
    today_total = sum(m.today_minutes for m in members if m.last_study_date == today)

    # 今日打卡人数
    today_checkins = (
        db.query(sa_func.count(StudyRoomCheckin.id))
        .filter(
            StudyRoomCheckin.room_id == room_id,
            cast(StudyRoomCheckin.created_at, Date) == today,
        )
        .scalar()
    ) or 0

    # 成员列表（简化）
    member_list = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        member_list.append({
            "user_id": m.user_id,
            "nickname": user.nickname if user else f"用户{m.user_id}",
            "avatar": user.avatar if user else None,
            "role": user.role if user else None,
            "study_minutes": m.study_minutes,
            "today_minutes": m.today_minutes if m.last_study_date == today else 0,
            "is_studying": m.is_studying,
            "is_owner": room.creator_id == m.user_id,
        })

    return ResponseOK(data={
        "total_members": len(members),
        "studying_count": studying_count,
        "today_total_minutes": today_total,
        "today_checkins": today_checkins,
        "daily_target_minutes": room.daily_target_minutes,
        "members": member_list,
    })


# ==================== 加入/离开 ====================

@router.post("/{room_id}/join", response_model=ResponseOK)
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """加入自习房间
    - 管理员/审核员：直接加入，拥有管理权限
    - 房主创建时已自动加入
    - 其他用户：申请加入，需房主/管理员/审核员审核通过后才能进入
    """
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")
    if room.status == "ended":
        raise HTTPException(status_code=400, detail="该房间已关闭")

    existing = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        if existing.status == "active":
            raise HTTPException(status_code=400, detail="您已加入该房间")
        elif existing.status == "pending":
            raise HTTPException(status_code=400, detail="您已申请加入，正在等待审核")
        elif existing.status == "kicked":
            raise HTTPException(status_code=403, detail="您已被移出该房间，无法再次加入")

    is_manager = current_user.role in ("admin", "auditor")

    if not is_manager:
        member_count = (
            db.query(StudyRoomMember)
            .filter(
                StudyRoomMember.room_id == room_id,
                StudyRoomMember.status == "active",
            )
            .count()
        )
        if member_count >= room.max_members:
            raise HTTPException(status_code=400, detail="房间人数已满")

    # 管理员/审核员直接加入；其他用户需审核
    member_status = "active" if is_manager else "pending"

    member = StudyRoomMember(
        room_id=room_id,
        user_id=current_user.id,
        study_minutes=0,
        is_studying=0,
        today_minutes=0,
        last_study_date=date.today(),
        status=member_status,
    )
    db.add(member)

    if is_manager:
        # 管理员加入发系统消息
        sys_msg = StudyRoomMessage(
            room_id=room_id,
            sender_id=current_user.id,
            content=f"【系统消息】{current_user.nickname or current_user.username} 加入了房间",
            zone="chat",
        )
        db.add(sys_msg)
        db.commit()
        return ResponseOK(message="已进入管理")
    else:
        # 普通用户申请加入，发系统消息通知管理员
        sys_msg = StudyRoomMessage(
            room_id=room_id,
            sender_id=current_user.id,
            content=f"【系统消息】{current_user.nickname or current_user.username} 申请加入房间，请管理员审核",
            zone="chat",
        )
        db.add(sys_msg)
        db.commit()
        return ResponseOK(message="申请已提交，等待房主或管理员审核")


@router.post("/{room_id}/leave", response_model=ResponseOK)
def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """离开自习房间（已加入的成员退出，待审核的取消申请）"""
    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == current_user.id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="您未加入该自习房间")

    is_pending = member.status == "pending"
    db.delete(member)

    if not is_pending:
        sys_msg = StudyRoomMessage(
            room_id=room_id,
            sender_id=current_user.id,
            content=f"【系统消息】{current_user.nickname or current_user.username} 离开了房间",
            zone="chat",
        )
        db.add(sys_msg)
    db.commit()
    return ResponseOK(message="已离开房间" if not is_pending else "已取消申请")


# ==================== 自习计时 ====================

@router.post("/{room_id}/start", response_model=ResponseOK)
def start_study(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """开始自习(设置 is_studying=1)"""
    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == current_user.id,
            StudyRoomMember.status == "active",
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="您未加入该自习房间或正在等待审核")
    if member.is_studying == 1:
        raise HTTPException(status_code=400, detail="您已在自习中")

    _reset_daily_if_needed(member)
    member.is_studying = 1
    db.commit()
    return ResponseOK(message="开始自习")


@router.post("/{room_id}/stop", response_model=ResponseOK)
def stop_study(
    room_id: int,
    payload: StudyMinutesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """结束自习(设置 is_studying=0)，并累加学习时长"""
    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == current_user.id,
            StudyRoomMember.status == "active",
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="您未加入该自习房间")

    _reset_daily_if_needed(member)
    member.is_studying = 0
    member.study_minutes += payload.study_minutes
    member.today_minutes += payload.study_minutes
    db.commit()
    return ResponseOK(
        data={
            "study_minutes": member.study_minutes,
            "today_minutes": member.today_minutes,
            "is_studying": member.is_studying,
        }
    )


# ==================== 成员管理 ====================

@router.get("/{room_id}/members", response_model=ResponseOK)
def get_room_members(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取房间成员列表"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    members = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.status == "active",
        )
        .order_by(StudyRoomMember.joined_at.asc())
        .all()
    )

    # 重置跨天数据
    for m in members:
        _reset_daily_if_needed(m)
    db.commit()

    today = date.today()
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append({
            "id": m.id,
            "user_id": m.user_id,
            "nickname": user.nickname if user else f"用户{m.user_id}",
            "avatar": user.avatar if user else None,
            "role": user.role if user else None,
            "username": user.username if user else "",
            "study_minutes": m.study_minutes,
            "today_minutes": m.today_minutes if m.last_study_date == today else 0,
            "is_studying": m.is_studying,
            "is_owner": room.creator_id == m.user_id,
            "joined_at": m.joined_at,
        })
    return ResponseOK(data=result)


# ==================== 群聊消息（支持分区） ====================

@router.get("/{room_id}/messages", response_model=ResponseOK)
def get_room_messages(
    room_id: int,
    zone: str = Query("chat", description="消息分区: chat=闲聊 study=自习"),
    before_id: int = Query(0, description="获取此ID之前的消息"),
    limit: int = Query(50, ge=1, le=100, description="每次获取条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取房间消息（支持按分区获取）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    if current_user.role not in ("admin", "auditor"):
        is_member = (
            db.query(StudyRoomMember)
            .filter(
                StudyRoomMember.room_id == room_id,
                StudyRoomMember.user_id == current_user.id,
                StudyRoomMember.status == "active",
            )
            .first()
        )
        if not is_member:
            raise HTTPException(status_code=403, detail="请先加入房间再查看消息")

    # zone=all 获取所有分区消息，否则按分区过滤
    query = db.query(StudyRoomMessage).filter(StudyRoomMessage.room_id == room_id)
    if zone != "all":
        query = query.filter(StudyRoomMessage.zone == zone)
    if before_id > 0:
        query = query.filter(StudyRoomMessage.id < before_id)

    messages = (
        query.order_by(StudyRoomMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()

    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append({
            "id": m.id,
            "room_id": m.room_id,
            "sender_id": m.sender_id,
            "sender_name": sender.nickname if sender else f"用户{m.sender_id}",
            "sender_avatar": sender.avatar if sender else None,
            "sender_role": sender.role if sender else None,
            "content": m.content,
            "zone": m.zone,
            "created_at": m.created_at,
            "is_system": m.content.startswith("【系统消息】"),
        })
    return ResponseOK(data=result)


@router.post("/{room_id}/messages", response_model=ResponseOK)
def send_room_message(
    room_id: int,
    payload: SendMessagePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """在房间内发送消息（支持指定分区）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")
    if room.status == "ended":
        raise HTTPException(status_code=400, detail="该房间已关闭，无法发送消息")

    if current_user.role not in ("admin", "auditor"):
        is_member = (
            db.query(StudyRoomMember)
            .filter(
                StudyRoomMember.room_id == room_id,
                StudyRoomMember.user_id == current_user.id,
                StudyRoomMember.status == "active",
            )
            .first()
        )
        if not is_member:
            raise HTTPException(status_code=403, detail="请先加入房间再发送消息")

    zone = payload.zone if payload.zone in ("chat", "study") else "chat"
    msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=payload.content,
        zone=zone,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return ResponseOK(data={
        "id": msg.id,
        "room_id": msg.room_id,
        "sender_id": msg.sender_id,
        "sender_name": current_user.nickname or current_user.username,
        "sender_avatar": current_user.avatar,
        "sender_role": current_user.role,
        "content": msg.content,
        "zone": msg.zone,
        "created_at": msg.created_at,
        "is_system": False,
    })


# ==================== 结构化打卡 ====================

@router.post("/{room_id}/checkin", response_model=ResponseOK)
def submit_checkin(
    room_id: int,
    payload: CheckinPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交结构化打卡记录"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == current_user.id,
            StudyRoomMember.status == "active",
        )
        .first()
    )
    if member is None and current_user.role not in ("admin", "auditor"):
        raise HTTPException(status_code=400, detail="请先加入房间再打卡")

    # 创建打卡记录
    checkin = StudyRoomCheckin(
        room_id=room_id,
        user_id=current_user.id,
        completed=payload.completed,
        incomplete=payload.incomplete,
        tomorrow_plan=payload.tomorrow_plan,
        mood=payload.mood,
        study_minutes=payload.study_minutes,
    )
    db.add(checkin)

    # 如果有学习时长，累加到成员记录
    if member and payload.study_minutes > 0:
        _reset_daily_if_needed(member)
        member.study_minutes += payload.study_minutes
        member.today_minutes += payload.study_minutes

    # 自习区发一条打卡消息
    summary_parts = []
    if payload.completed:
        summary_parts.append(f"✅完成: {payload.completed[:50]}")
    if payload.tomorrow_plan:
        summary_parts.append(f"🎯明日: {payload.tomorrow_plan[:50]}")
    if payload.study_minutes > 0:
        summary_parts.append(f"⏱学习{payload.study_minutes}分钟")

    checkin_msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=f"【打卡】{current_user.nickname or current_user.username} 完成了今日打卡 {' | '.join(summary_parts)}",
        zone="study",
    )
    db.add(checkin_msg)
    db.commit()
    db.refresh(checkin)

    return ResponseOK(data={
        "id": checkin.id,
        "completed": checkin.completed,
        "incomplete": checkin.incomplete,
        "tomorrow_plan": checkin.tomorrow_plan,
        "mood": checkin.mood,
        "study_minutes": checkin.study_minutes,
        "created_at": checkin.created_at,
    })


@router.get("/{room_id}/checkins", response_model=ResponseOK)
def get_room_checkins(
    room_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取房间打卡记录列表"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    query = db.query(StudyRoomCheckin).filter(StudyRoomCheckin.room_id == room_id)
    total = query.count()
    checkins = (
        query.order_by(StudyRoomCheckin.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for c in checkins:
        user = db.query(User).filter(User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "nickname": user.nickname if user else f"用户{c.user_id}",
            "avatar": user.avatar if user else None,
            "role": user.role if user else None,
            "completed": c.completed,
            "incomplete": c.incomplete,
            "tomorrow_plan": c.tomorrow_plan,
            "mood": c.mood,
            "study_minutes": c.study_minutes,
            "created_at": c.created_at,
        })
    return ResponseOK(data=result, total=total)


# ==================== 房间公告 ====================

@router.put("/{room_id}/announcement", response_model=ResponseOK)
def update_announcement(
    room_id: int,
    payload: AnnouncementPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新房间公告（仅群主/管理员/审核员）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    if current_user.role not in ("admin", "auditor") and room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅群主/管理员可设置公告")

    room.announcement = payload.announcement
    db.commit()

    # 系统消息
    sys_msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=f"【系统消息】{current_user.nickname or current_user.username} 更新了房间公告",
        zone="chat",
    )
    db.add(sys_msg)
    db.commit()

    return ResponseOK(message="公告已更新")


# ==================== 管理功能 ====================

@router.get("/{room_id}/pending", response_model=ResponseOK)
def get_pending_members(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取待审核成员列表（仅群主/管理员/审核员可查看）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    if current_user.role not in ("admin", "auditor") and room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅群主/管理员/审核员可查看")

    members = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.status == "pending",
        )
        .order_by(StudyRoomMember.joined_at.asc())
        .all()
    )

    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append({
            "id": m.id,
            "user_id": m.user_id,
            "nickname": user.nickname if user else f"用户{m.user_id}",
            "avatar": user.avatar if user else None,
            "role": user.role if user else None,
            "username": user.username if user else "",
            "joined_at": m.joined_at,
        })
    return ResponseOK(data=result)


@router.post("/{room_id}/approve/{user_id}", response_model=ResponseOK)
def approve_member(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """审核通过成员加入申请（仅群主/管理员/审核员可操作）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    if current_user.role not in ("admin", "auditor") and room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅群主/管理员/审核员可审核")

    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == user_id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="该用户未申请加入")
    if member.status != "pending":
        raise HTTPException(status_code=400, detail="该用户不在待审核状态")

    # 检查人数是否已满
    active_count = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.status == "active",
        )
        .count()
    )
    if active_count >= room.max_members:
        raise HTTPException(status_code=400, detail="房间人数已满，无法通过审核")

    member.status = "active"

    target_user = db.query(User).filter(User.id == user_id).first()
    target_name = target_user.nickname if target_user else f"用户{user_id}"

    sys_msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=f"【系统消息】{target_name} 已通过审核，加入房间",
        zone="chat",
    )
    db.add(sys_msg)
    db.commit()

    return ResponseOK(message=f"已通过 {target_name} 的加入申请")


@router.post("/{room_id}/reject/{user_id}", response_model=ResponseOK)
def reject_member(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """拒绝成员加入申请（仅群主/管理员/审核员可操作）"""
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    if current_user.role not in ("admin", "auditor") and room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅群主/管理员/审核员可审核")

    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == user_id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="该用户未申请加入")
    if member.status != "pending":
        raise HTTPException(status_code=400, detail="该用户不在待审核状态")

    target_user = db.query(User).filter(User.id == user_id).first()
    target_name = target_user.nickname if target_user else f"用户{user_id}"

    db.delete(member)

    sys_msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=f"【系统消息】{target_name} 的加入申请已被拒绝",
        zone="chat",
    )
    db.add(sys_msg)
    db.commit()

    return ResponseOK(message=f"已拒绝 {target_name} 的加入申请")


@router.delete("/{room_id}/members/{user_id}", response_model=ResponseOK)
def kick_member(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """踢出房间成员（仅管理员/审核员/群主可操作），踢出后不可再次加入"""
    if current_user.role not in ("admin", "auditor"):
        room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
        if not room or room.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权操作，仅管理员/审核员/群主可踢人")

    member = (
        db.query(StudyRoomMember)
        .filter(
            StudyRoomMember.room_id == room_id,
            StudyRoomMember.user_id == user_id,
        )
        .first()
    )
    if member is None:
        raise HTTPException(status_code=400, detail="该用户不在房间内")
    if member.status == "kicked":
        raise HTTPException(status_code=400, detail="该用户已被踢出")

    # 不能踢群主
    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room and room.creator_id == user_id:
        raise HTTPException(status_code=400, detail="不能踢出房主")

    target_user = db.query(User).filter(User.id == user_id).first()
    target_name = target_user.nickname if target_user else f"用户{user_id}"

    # 设置为 kicked 状态，而不是删除，防止再次加入
    member.status = "kicked"
    member.is_studying = 0

    sys_msg = StudyRoomMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=f"【系统消息】{target_name} 被移出房间",
        zone="chat",
    )
    db.add(sys_msg)
    db.commit()

    return ResponseOK(message=f"已将 {target_name} 移出房间")


@router.put("/{room_id}/close", response_model=ResponseOK)
def close_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关闭/解散房间（仅管理员/审核员可操作）"""
    if current_user.role not in ("admin", "auditor"):
        raise HTTPException(status_code=403, detail="无权操作，仅管理员/审核员可关闭房间")

    room = db.query(StudyRoom).filter(StudyRoom.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="房间不存在")

    room.status = "ended"
    db.commit()

    return ResponseOK(message="房间已关闭")


@router.get("/admin/all", response_model=ResponseOK)
def get_all_rooms_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有房间列表（仅管理员/审核员）"""
    if current_user.role not in ("admin", "auditor"):
        raise HTTPException(status_code=403, detail="无权访问")

    rooms = (
        db.query(StudyRoom)
        .order_by(StudyRoom.created_at.desc())
        .all()
    )
    return ResponseOK(
        data=[_room_to_dict(r, db, current_user.id, current_user.role) for r in rooms]
    )


# ==================== 我的打卡档案 ====================

@router.get("/my-checkins", response_model=ResponseOK)
def get_my_checkins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我的所有打卡记录（用于打卡档案页）"""
    checkins = (
        db.query(StudyRoomCheckin, StudyRoom)
        .join(StudyRoom, StudyRoomCheckin.room_id == StudyRoom.id)
        .filter(StudyRoomCheckin.user_id == current_user.id)
        .order_by(StudyRoomCheckin.created_at.desc())
        .limit(100)
        .all()
    )

    result = []
    total_minutes = 0
    for c, room in checkins:
        total_minutes += c.study_minutes
        result.append({
            "id": c.id,
            "room_id": c.room_id,
            "room_name": room.name,
            "completed": c.completed,
            "incomplete": c.incomplete,
            "tomorrow_plan": c.tomorrow_plan,
            "mood": c.mood,
            "study_minutes": c.study_minutes,
            "created_at": c.created_at,
        })

    # 统计本周学习时长
    today = date.today()
    week_start = today.toordinal() - today.weekday()
    week_dates = [date.fromordinal(week_start + i) for i in range(7)]
    week_minutes = [0] * 7
    for c, room in checkins:
        c_date = c.created_at.date() if c.created_at else None
        if c_date in week_dates:
            week_minutes[week_dates.index(c_date)] += c.study_minutes

    return ResponseOK(data={
        "checkins": result,
        "total_checkins": len(result),
        "total_minutes": total_minutes,
        "week_minutes": week_minutes,
        "week_dates": [d.isoformat() for d in week_dates],
    })
