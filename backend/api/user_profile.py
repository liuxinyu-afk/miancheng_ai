"""
用户公开主页路由
提供用户公开资料、推荐好友、用户发布的资源/成果帖列表等接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_, func, case
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.market_resource import MarketResource
from models.achievement import AchievementPost
from models.study_room import StudyRoomMember
from models.friendship import Friendship
from schemas.common import ResponseOK, PageResponse
from utils.deps import get_current_user

router = APIRouter(prefix="/api/user", tags=["用户公开主页"])


def _friend_status(db: Session, current_user_id: int, target_user_id: int) -> str:
    """计算当前用户与目标用户的好友关系状态

    返回值含义：
        - self: 自己
        - none: 无好友关系
        - friend: 已是好友
        - pending_sent: 我发出的请求待处理
        - pending_received: 对方发给我的请求待处理
    """
    if current_user_id == target_user_id:
        return "self"

    friendship = (
        db.query(Friendship)
        .filter(
            or_(
                and_(
                    Friendship.requester_id == current_user_id,
                    Friendship.receiver_id == target_user_id,
                ),
                and_(
                    Friendship.requester_id == target_user_id,
                    Friendship.receiver_id == current_user_id,
                ),
            ),
        )
        .first()
    )

    if friendship is None:
        return "none"
    if friendship.status == "accepted":
        return "friend"
    if friendship.status == "pending":
        return "pending_sent" if friendship.requester_id == current_user_id else "pending_received"
    # rejected 视为无关系
    return "none"


# ==================== 用户公开资料 ====================

@router.get("/profile/{user_id}", response_model=ResponseOK, summary="获取用户公开资料")
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定用户的公开主页资料

    包含：基本信息、已发布资源概览、成果帖概览、累计学习时长、与当前用户的好友状态。
    注意：公开资料仅返回已审核通过的内容，且不包含 password / real_name 等敏感字段。
    """
    user = db.query(User).filter(User.id == user_id, User.status == 1).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 基本信息：仅暴露安全字段，不返回 password / real_name
    basic_info = {
        "id": user.id,
        "nickname": user.nickname,
        "username": user.username,
        "avatar": user.avatar,
        "role": user.role,
        "created_at": user.created_at,
        "cert_status": getattr(user, "cert_status", None),
        "is_teacher_certified": getattr(user, "cert_status", None) == "approved" and user.role == "teacher",
    }

    # 已审核通过的资源：总数 + 最新5条
    resource_query = db.query(MarketResource).filter(
        MarketResource.publisher_id == user_id,
        MarketResource.audit_status == "approved",
    )
    resource_count = resource_query.count()
    latest_resources = (
        resource_query.order_by(MarketResource.created_at.desc())
        .limit(5)
        .all()
    )
    resources = [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "created_at": r.created_at,
            "view_count": r.view_count,
        }
        for r in latest_resources
    ]

    # 已审核通过的成果帖：总数 + 最新5条（内容仅取预览）
    post_query = db.query(AchievementPost).filter(
        AchievementPost.user_id == user_id,
        AchievementPost.audit_status == "approved",
    )
    post_count = post_query.count()
    latest_posts = (
        post_query.order_by(AchievementPost.created_at.desc())
        .limit(5)
        .all()
    )
    posts = [
        {
            "id": p.id,
            "content": (p.content[:100] if p.content else ""),
            "created_at": p.created_at,
        }
        for p in latest_posts
    ]

    # 累计学习时长（分钟）：汇总该用户在所有自习房间的学习时长
    total_study_minutes = (
        db.query(func.coalesce(func.sum(StudyRoomMember.study_minutes), 0))
        .filter(StudyRoomMember.user_id == user_id)
        .scalar()
    )

    # 与当前用户的好友状态
    friend_status = _friend_status(db, current_user.id, user_id)

    return ResponseOK(data={
        "basic_info": basic_info,
        "resource_count": resource_count,
        "resources": resources,
        "post_count": post_count,
        "posts": posts,
        "total_study_minutes": total_study_minutes,
        "friend_status": friend_status,
    })


# ==================== 推荐好友 ====================

@router.get("/recommend", response_model=ResponseOK, summary="获取推荐好友")
def recommend_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取推荐好友列表（最多10个）

    规则：
        - 排除当前用户及已是好友的用户
        - 同角色用户优先，其次其他角色
        - 按已发布(已审核通过)资源数量降序排列
    返回：id, nickname, avatar, role, resource_count, achievement_count
    """
    # 收集当前用户已通过的好友ID
    friend_rows = (
        db.query(Friendship)
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.receiver_id == current_user.id,
            ),
            Friendship.status == "accepted",
        )
        .all()
    )
    friend_ids = {
        (f.receiver_id if f.requester_id == current_user.id else f.requester_id)
        for f in friend_rows
    }
    # 排除当前用户及已有好友
    exclude_ids = friend_ids | {current_user.id}

    # 子查询：每个用户已审核通过的资源数量
    resource_count_sub = (
        db.query(
            MarketResource.publisher_id.label("uid"),
            func.count(MarketResource.id).label("cnt"),
        )
        .filter(MarketResource.audit_status == "approved")
        .group_by(MarketResource.publisher_id)
        .subquery()
    )

    # 子查询：每个用户已审核通过的成果帖数量
    post_count_sub = (
        db.query(
            AchievementPost.user_id.label("uid"),
            func.count(AchievementPost.id).label("cnt"),
        )
        .filter(AchievementPost.audit_status == "approved")
        .group_by(AchievementPost.user_id)
        .subquery()
    )

    # 同角色优先（0=同角色, 1=其他角色）
    role_priority = case(
        (User.role == current_user.role, 0),
        else_=1,
    )

    rows = (
        db.query(
            User,
            func.coalesce(resource_count_sub.c.cnt, 0).label("resource_count"),
            func.coalesce(post_count_sub.c.cnt, 0).label("achievement_count"),
        )
        .outerjoin(resource_count_sub, resource_count_sub.c.uid == User.id)
        .outerjoin(post_count_sub, post_count_sub.c.uid == User.id)
        .filter(User.id.notin_(list(exclude_ids)), User.status == 1)
        .order_by(role_priority, func.coalesce(resource_count_sub.c.cnt, 0).desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "id": u.id,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "role": u.role,
            "resource_count": resource_count,
            "achievement_count": achievement_count,
        }
        for u, resource_count, achievement_count in rows
    ]

    return ResponseOK(data=result)


# ==================== 用户发布的资源列表 ====================

@router.get("/{user_id}/resources", response_model=PageResponse, summary="获取用户发布的资源列表")
def get_user_resources(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
):
    """分页获取指定用户已审核通过的资源列表"""
    query = db.query(MarketResource).filter(
        MarketResource.publisher_id == user_id,
        MarketResource.audit_status == "approved",
    )
    total = query.count()
    resources = (
        query.order_by(MarketResource.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "content": r.content,
            "attachment_url": r.attachment_url,
            "view_count": r.view_count,
            "created_at": r.created_at,
        }
        for r in resources
    ]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)


# ==================== 用户成果帖列表 ====================

@router.get("/{user_id}/posts", response_model=PageResponse, summary="获取用户成果帖列表")
def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
):
    """分页获取指定用户已审核通过的成果帖列表"""
    query = db.query(AchievementPost).filter(
        AchievementPost.user_id == user_id,
        AchievementPost.audit_status == "approved",
    )
    total = query.count()
    posts = (
        query.order_by(AchievementPost.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [
        {
            "id": p.id,
            "content": p.content,
            "images": p.images,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at,
        }
        for p in posts
    ]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)
