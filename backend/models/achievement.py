"""成果帖子、评论、点赞表模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, Enum, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AchievementPost(Base):
    __tablename__ = "achievement_post"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="图文内容")
    images: Mapped[list | None] = mapped_column(JSON, default=None, comment="图片附件JSON数组")
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="点赞数量")
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="评论数量")
    audit_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected"), nullable=False, default="pending", comment="审核状态"
    )
    reject_reason: Mapped[str | None] = mapped_column(String(500), default=None, comment="驳回理由")
    # V8 新增字段
    tags: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="内容标签，逗号分隔")
    is_anonymous: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="0=实名 1=匿名")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AchievementComment(Base):
    __tablename__ = "achievement_comment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("achievement_post.id"), nullable=False, comment="帖子ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="评论人ID")
    content: Mapped[str] = mapped_column(String(1000), nullable=False, comment="评论内容")
    is_teacher: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="是否教师点评")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="父评论ID（回复用）")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AchievementLike(Base):
    __tablename__ = "achievement_like"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("achievement_post.id"), nullable=False, comment="帖子ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="用户ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
