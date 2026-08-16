"""
勋章系统路由
自动检测用户是否满足勋章条件并发放
"""
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.badge import Badge, UserBadge
from models.market_resource import MarketResource
from models.achievement import AchievementPost
from models.study_room import StudyRoom, StudyRoomMember, StudyRoomCheckin
from models.friendship import Friendship
from models.note import Note
from models.task_package import TaskPackage
from models.task_item import TaskItem
from models.private_message import PrivateMessage
from models.study_room_message import StudyRoomMessage
from schemas.common import ResponseOK
from utils.deps import get_current_user

router = APIRouter(prefix="/api/badges", tags=["勋章系统"])


def _check_and_award(db: Session, user: User) -> list[dict]:
    """检查用户是否满足勋章条件，发放新勋章，返回新获得的勋章列表"""
    badges = db.query(Badge).all()
    existing = {ub.badge_id for ub in db.query(UserBadge).filter(UserBadge.user_id == user.id).all()}
    newly_awarded = []

    for badge in badges:
        if badge.id in existing:
            continue

        earned = False
        ct = badge.condition_type
        cv = badge.condition_value

        if ct == "study_minutes":
            total = db.query(func.sum(StudyRoomMember.study_minutes)).filter(
                StudyRoomMember.user_id == user.id
            ).scalar() or 0
            earned = total >= cv

        elif ct == "checkin_count":
            count = db.query(StudyRoomCheckin).filter(StudyRoomCheckin.user_id == user.id).count()
            earned = count >= cv

        elif ct == "friend_count":
            count = db.query(Friendship).filter(
                Friendship.status == "accepted",
                (Friendship.requester_id == user.id) | (Friendship.receiver_id == user.id),
            ).count()
            earned = count >= cv

        elif ct == "like_received":
            # 收到的点赞数（成果帖子的点赞）
            posts = db.query(AchievementPost).filter(AchievementPost.user_id == user.id).all()
            total = sum(p.like_count for p in posts)
            earned = total >= cv

        elif ct == "resource_count":
            count = db.query(MarketResource).filter(
                MarketResource.publisher_id == user.id,
                MarketResource.audit_status == "approved",
            ).count()
            earned = count >= cv

        elif ct == "post_count":
            count = db.query(AchievementPost).filter(
                AchievementPost.user_id == user.id,
                AchievementPost.audit_status == "approved",
            ).count()
            earned = count >= cv

        elif ct == "room_count":
            count = db.query(StudyRoom).filter(StudyRoom.creator_id == user.id).count()
            earned = count >= cv

        elif ct == "register_days":
            if user.created_at:
                days = (datetime.now() - user.created_at).days
                earned = days >= cv

        elif ct == "note_count":
            count = db.query(Note).filter(Note.user_id == user.id).count()
            earned = count >= cv

        elif ct == "task_count":
            count = db.query(TaskPackage).filter(TaskPackage.publisher_id == user.id).count()
            earned = count >= cv

        elif ct == "ai_task_count":
            # TaskItem 通过 package_id 关联 TaskPackage，TaskPackage 用 publisher_id 关联用户
            count = db.query(TaskItem).join(
                TaskPackage, TaskItem.package_id == TaskPackage.id
            ).filter(TaskPackage.publisher_id == user.id).count()
            earned = count >= cv

        elif ct == "message_sent":
            count = db.query(PrivateMessage).filter(PrivateMessage.sender_id == user.id).count()
            earned = count >= cv

        elif ct == "room_message_count":
            count = db.query(StudyRoomMessage).filter(StudyRoomMessage.sender_id == user.id).count()
            earned = count >= cv

        elif ct == "room_join_count":
            count = db.query(StudyRoomMember).filter(StudyRoomMember.user_id == user.id).count()
            earned = count >= cv

        elif ct == "comment_count":
            from models.achievement import AchievementComment
            count = db.query(AchievementComment).filter(AchievementComment.user_id == user.id).count()
            earned = count >= cv

        elif ct == "public_note_count":
            count = db.query(Note).filter(Note.user_id == user.id, Note.is_public == 1).count()
            earned = count >= cv

        if earned:
            ub = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(ub)
            newly_awarded.append({
                "id": badge.id,
                "name": badge.name,
                "icon": badge.icon,
                "description": badge.description,
            })

    if newly_awarded:
        db.commit()

    return newly_awarded


@router.get("/my", response_model=ResponseOK, summary="获取我的勋章")
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的勋章列表，同时自动检测并发放新勋章"""
    # 自动检测
    newly = _check_and_award(db, current_user)

    # 查询所有勋章
    all_badges = db.query(Badge).all()
    user_badge_ids = {ub.badge_id for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()}

    result = []
    for badge in all_badges:
        result.append({
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "category": badge.category,
            "condition_type": badge.condition_type,
            "condition_value": badge.condition_value,
            "earned": badge.id in user_badge_ids,
        })

    return ResponseOK(data={"badges": result, "newly_awarded": newly})


@router.get("/user/{user_id}", response_model=ResponseOK, summary="获取指定用户的勋章")
def get_user_badges(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定用户的勋章（仅展示已获得的）"""
    user_badges = (
        db.query(UserBadge, Badge)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == user_id)
        .all()
    )
    result = []
    for ub, badge in user_badges:
        result.append({
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "category": badge.category,
            "awarded_at": ub.awarded_at,
        })
    return ResponseOK(data=result)
