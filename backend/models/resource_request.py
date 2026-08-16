"""资料求助广场模型"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ResourceRequest(Base):
    """交流广场帖子"""
    __tablename__ = "resource_request"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="发布者ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="帖子标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="详细描述")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="其他", comment="分类: 考研/编程/英语/论文/职业/其他")
    tags: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="标签，逗号分隔")
    images: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="图片URL列表，逗号分隔")
    reply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="回复数量")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="浏览次数")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", comment="open=待解决 solved=已解决 closed=已关闭")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ResourceReply(Base):
    """交流广场回复"""
    __tablename__ = "resource_reply"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("resource_request.id"), nullable=False, comment="帖子ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, comment="回复者ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="回复内容")
    resource_link: Mapped[str] = mapped_column(String(500), nullable=False, default="", comment="资料链接（网盘/URL）")
    images: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="图片URL列表，逗号分隔")
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False, default="link", comment="link=链接 file=文件 text=文字说明")
    is_accepted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="是否被采纳 0=否 1=是")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
