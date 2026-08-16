"""
成果社区路由 - 帖子、评论、点赞、消息通知、学习排行榜
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from models.user import User
from models.achievement import AchievementPost, AchievementComment, AchievementLike
from models.misc import Message
from models.study_room import StudyRoomMember
from models.market_resource import MarketResource
from schemas.common import ResponseOK, PageResponse
from schemas.achievement import PostCreate, PostOut, CommentCreate, CommentOut
from utils.deps import get_current_user

router = APIRouter(prefix="/api/achievement", tags=["成果社区"])


# ==================== 帖子相关 ====================

@router.post("/posts", response_model=ResponseOK)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发布成果帖子(需审核，初始状态为 pending)"""
    post = AchievementPost(
        user_id=current_user.id,
        content=payload.content,
        images=payload.images,
        audit_status="pending",
        tags=payload.tags,
        is_anonymous=payload.is_anonymous,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return ResponseOK(data=PostOut.model_validate(post).model_dump())


@router.get("/posts", response_model=PageResponse)
def get_posts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    audit_status: str | None = Query(None, description="审核状态筛选: approved/pending/rejected"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取帖子列表(分页)，支持按审核状态筛选"""
    query = db.query(AchievementPost)

    if audit_status:
        if audit_status == "approved":
            # 已通过：所有人可见
            query = query.filter(AchievementPost.audit_status == "approved")
        else:
            # 审核中/已驳回：只显示当前用户自己的帖子
            query = query.filter(
                AchievementPost.audit_status == audit_status,
                AchievementPost.user_id == current_user.id,
            )
    else:
        # 全部：显示已通过的 + 当前用户自己的所有状态
        from sqlalchemy import or_
        query = query.filter(
            or_(
                AchievementPost.audit_status == "approved",
                AchievementPost.user_id == current_user.id,
            )
        )

    total = query.count()
    posts = (
        query.order_by(AchievementPost.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 构造返回数据，附带作者信息
    data = []
    for p in posts:
        author = db.query(User).filter(User.id == p.user_id).first()
        item = {
            "id": p.id,
            "user_id": p.user_id,
            "content": p.content,
            "images": p.images,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "audit_status": p.audit_status,
            "created_at": p.created_at,
            "author_name": (author.nickname or author.username) if author else f"用户{p.user_id}",
            "author_role": author.role if author else None,
            "author_avatar": author.avatar if author else None,
            "tags": p.tags or "",
            "is_anonymous": p.is_anonymous or 0,
            "reject_reason": p.reject_reason,
        }
        # 匿名发布处理
        if p.is_anonymous == 1 and p.user_id != current_user.id:
            item["author_name"] = "匿名用户"
            item["author_role"] = None
            item["author_avatar"] = None
        data.append(item)

    return PageResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/posts/{post_id}", response_model=ResponseOK)
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
):
    """获取帖子详情"""
    post = (
        db.query(AchievementPost)
        .filter(AchievementPost.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return ResponseOK(data=PostOut.model_validate(post).model_dump())


@router.get("/my-posts", response_model=ResponseOK)
def get_my_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我发布的帖子(含所有审核状态)"""
    posts = (
        db.query(AchievementPost)
        .filter(AchievementPost.user_id == current_user.id)
        .order_by(AchievementPost.created_at.desc())
        .all()
    )
    return ResponseOK(
        data=[PostOut.model_validate(p).model_dump() for p in posts]
    )


@router.delete("/posts/{post_id}", response_model=ResponseOK)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除帖子(只能删除自己的帖子)"""
    post = (
        db.query(AchievementPost)
        .filter(AchievementPost.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人的帖子")

    # 同步删除关联的评论和点赞记录
    db.query(AchievementComment).filter(
        AchievementComment.post_id == post_id
    ).delete(synchronize_session=False)
    db.query(AchievementLike).filter(
        AchievementLike.post_id == post_id
    ).delete(synchronize_session=False)
    db.delete(post)
    db.commit()
    return ResponseOK(message="删除成功")


# ==================== 点赞相关 ====================

@router.post("/posts/{post_id}/like", response_model=ResponseOK)
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """点赞帖子(已点赞则取消)"""
    post = (
        db.query(AchievementPost)
        .filter(AchievementPost.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 查询当前用户是否已点赞该帖子
    existing = (
        db.query(AchievementLike)
        .filter(
            AchievementLike.post_id == post_id,
            AchievementLike.user_id == current_user.id,
        )
        .first()
    )

    if existing:
        # 已点赞 -> 取消点赞
        db.delete(existing)
        post.like_count = max(post.like_count - 1, 0)
        db.commit()
        return ResponseOK(data={"liked": False, "like_count": post.like_count})
    else:
        # 未点赞 -> 创建点赞记录
        like = AchievementLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        post.like_count += 1

        # 给帖子作者发送点赞通知（不给自己发）
        if post.user_id != current_user.id:
            liker_name = current_user.nickname or current_user.username
            msg = Message(
                user_id=post.user_id,
                title="收到新点赞",
                content=f"{liker_name} 赞了你的成果",
                msg_type="like",
                is_read=0,
                related_id=post_id,
                sender_id=current_user.id,
            )
            db.add(msg)

        db.commit()
        return ResponseOK(data={"liked": True, "like_count": post.like_count})


# ==================== 评论相关 ====================

@router.post("/posts/{post_id}/comments", response_model=ResponseOK)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发表评论(教师角色自动标记为教师点评)"""
    post = (
        db.query(AchievementPost)
        .filter(AchievementPost.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")

    comment = AchievementComment(
        post_id=post_id,
        user_id=current_user.id,
        content=payload.content,
        # 教师角色发表的评论标记为教师点评
        is_teacher=1 if current_user.role == "teacher" else 0,
        parent_id=payload.parent_id,
    )
    db.add(comment)
    post.comment_count += 1

    # 给帖子作者发送评论通知（不给自己发）
    if post.user_id != current_user.id:
        commenter_name = current_user.nickname or current_user.username
        msg = Message(
            user_id=post.user_id,
            title="收到新评论",
            content=f"{commenter_name} 评论了你的成果：{payload.content[:50]}",
            msg_type="comment",
            is_read=0,
            related_id=post_id,
            sender_id=current_user.id,
        )
        db.add(msg)

    db.commit()
    db.refresh(comment)
    return ResponseOK(data=CommentOut.model_validate(comment).model_dump())


@router.get("/posts/{post_id}/comments", response_model=ResponseOK)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
):
    """获取帖子评论列表（含评论者昵称）"""
    post = (
        db.query(AchievementPost)
        .filter(AchievementPost.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")

    comments = (
        db.query(AchievementComment, User.nickname, User.username, User.role)
        .join(User, AchievementComment.user_id == User.id)
        .filter(AchievementComment.post_id == post_id)
        .order_by(AchievementComment.created_at.asc())
        .all()
    )
    result = []
    for c, nickname, username, role in comments:
        item = CommentOut.model_validate(c).model_dump()
        item["author_name"] = nickname or username
        item["author_role"] = role
        result.append(item)
    return ResponseOK(data=result)


# ==================== 消息通知 ====================

@router.get("/messages", response_model=ResponseOK)
def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的消息通知列表（含发送者昵称和帖子摘要）"""
    messages = (
        db.query(Message)
        .filter(Message.user_id == current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    result = []
    for m in messages:
        item = {
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "msg_type": m.msg_type,
            "is_read": m.is_read,
            "created_at": m.created_at,
            "related_id": m.related_id,
            "sender_id": m.sender_id,
            "sender_name": None,
            "sender_role": None,
            "post_content": None,
        }
        # 查询发送者信息
        if m.sender_id:
            sender = db.query(User).filter(User.id == m.sender_id).first()
            if sender:
                item["sender_name"] = sender.nickname or sender.username
                item["sender_role"] = sender.role
        # 查询关联帖子摘要
        if m.related_id:
            post = db.query(AchievementPost).filter(AchievementPost.id == m.related_id).first()
            if post:
                item["post_content"] = post.content[:100] if post.content else ""
        result.append(item)
    return ResponseOK(data=result)


@router.get("/messages/{message_id}/detail", response_model=ResponseOK)
def get_message_detail(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取消息详情（含完整关联信息：发送者、帖子、评论内容等）"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="消息不存在")
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此消息")

    data = {
        "id": message.id,
        "title": message.title,
        "content": message.content,
        "msg_type": message.msg_type,
        "is_read": message.is_read,
        "created_at": message.created_at,
        "related_id": message.related_id,
        "sender_id": message.sender_id,
        "sender_name": None,
        "sender_role": None,
        "post": None,
        "comments": [],
    }

    # 发送者信息
    if message.sender_id:
        sender = db.query(User).filter(User.id == message.sender_id).first()
        if sender:
            data["sender_name"] = sender.nickname or sender.username
            data["sender_role"] = sender.role

    # 关联帖子信息
    if message.related_id:
        post = db.query(AchievementPost).filter(AchievementPost.id == message.related_id).first()
        if post:
            data["post"] = {
                "id": post.id,
                "content": post.content,
                "images": post.images,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "audit_status": post.audit_status,
                "created_at": post.created_at,
            }
            # 如果是评论消息，获取该用户在此帖子上的评论
            if message.msg_type == "comment" and message.sender_id:
                sender_comments = (
                    db.query(AchievementComment)
                    .filter(
                        AchievementComment.post_id == post.id,
                        AchievementComment.user_id == message.sender_id,
                    )
                    .order_by(AchievementComment.created_at.desc())
                    .limit(5)
                    .all()
                )
                data["comments"] = [
                    {
                        "id": c.id,
                        "content": c.content,
                        "is_teacher": c.is_teacher,
                        "created_at": c.created_at,
                    }
                    for c in sender_comments
                ]

    # 自动标记为已读
    if message.is_read == 0:
        message.is_read = 1
        db.commit()

    return ResponseOK(data=data)


@router.put("/messages/{message_id}/read", response_model=ResponseOK)
def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记消息已读"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="消息不存在")
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此消息")

    message.is_read = 1
    db.commit()
    return ResponseOK(message="已标记为已读")


@router.put("/messages/read-all", response_model=ResponseOK)
def mark_all_messages_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """一键清除消息提示（标记所有消息为已读，消息本身不删除）"""
    db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == 0,
    ).update({Message.is_read: 1})
    db.commit()
    return ResponseOK(message="已清除所有消息提示")


# ==================== 学习排行榜 ====================

@router.get("/leaderboard", response_model=ResponseOK, summary="学习排行榜")
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取学习排行榜，展示学习时长 TOP 10 的用户"""
    # 按学习时长汇总
    study_sub = (
        db.query(
            StudyRoomMember.user_id.label("uid"),
            func.sum(StudyRoomMember.study_minutes).label("total_minutes"),
        )
        .group_by(StudyRoomMember.user_id)
        .subquery()
    )

    # 成果帖数子查询
    post_sub = (
        db.query(
            AchievementPost.user_id.label("uid"),
            func.count(AchievementPost.id).label("post_count"),
        )
        .filter(AchievementPost.audit_status == "approved")
        .group_by(AchievementPost.user_id)
        .subquery()
    )

    # 资源数子查询
    resource_sub = (
        db.query(
            MarketResource.publisher_id.label("uid"),
            func.count(MarketResource.id).label("resource_count"),
        )
        .filter(MarketResource.audit_status == "approved")
        .group_by(MarketResource.publisher_id)
        .subquery()
    )

    rows = (
        db.query(
            User,
            func.coalesce(study_sub.c.total_minutes, 0).label("study_minutes"),
            func.coalesce(post_sub.c.post_count, 0).label("post_count"),
            func.coalesce(resource_sub.c.resource_count, 0).label("resource_count"),
        )
        .outerjoin(study_sub, study_sub.c.uid == User.id)
        .outerjoin(post_sub, post_sub.c.uid == User.id)
        .outerjoin(resource_sub, resource_sub.c.uid == User.id)
        .filter(User.status == 1)
        .order_by(desc(func.coalesce(study_sub.c.total_minutes, 0)))
        .limit(10)
        .all()
    )

    result = []
    for rank, (user, study_min, post_cnt, res_cnt) in enumerate(rows, 1):
        result.append({
            "rank": rank,
            "user_id": user.id,
            "nickname": user.nickname or user.username,
            "avatar": user.avatar,
            "role": user.role,
            "study_minutes": study_min or 0,
            "post_count": post_cnt or 0,
            "resource_count": res_cnt or 0,
            "is_me": user.id == current_user.id,
        })

    return ResponseOK(data=result)


# ==================== 成果统计 ====================

@router.get("/stats", response_model=ResponseOK, summary="成果社区统计")
def get_achievement_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取成果社区统计数据"""
    total_posts = db.query(AchievementPost).filter(
        AchievementPost.audit_status == "approved"
    ).count()

    total_likes = db.query(func.sum(AchievementPost.like_count)).filter(
        AchievementPost.audit_status == "approved"
    ).scalar() or 0

    total_comments = db.query(func.sum(AchievementPost.comment_count)).filter(
        AchievementPost.audit_status == "approved"
    ).scalar() or 0

    # 今日新发布
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_posts = db.query(AchievementPost).filter(
        AchievementPost.created_at >= today_start
    ).count()

    # 我的成果
    my_posts = db.query(AchievementPost).filter(
        AchievementPost.user_id == current_user.id
    ).count()
    my_likes = db.query(func.sum(AchievementPost.like_count)).filter(
        AchievementPost.user_id == current_user.id
    ).scalar() or 0

    return ResponseOK(data={
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "today_posts": today_posts,
        "my_posts": my_posts,
        "my_likes": my_likes,
    })
