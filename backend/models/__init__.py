"""
ORM 模型统一导出
导入此模块即可使用所有数据表模型
"""
from models.user import User
from models.task_package import TaskPackage
from models.task_item import TaskItem
from models.market_resource import MarketResource
from models.check_record import CheckRecord
from models.note import Note
from models.achievement import AchievementPost, AchievementComment, AchievementLike
from models.audit_log import AuditLog
from models.study_room import StudyRoom, StudyRoomMember
from models.misc import UserFavorite, Message
from models.resource_request import ResourceRequest, ResourceReply
from models.feedback import Feedback

__all__ = [
    "User",
    "TaskPackage",
    "TaskItem",
    "MarketResource",
    "CheckRecord",
    "Note",
    "AchievementPost",
    "AchievementComment",
    "AchievementLike",
    "AuditLog",
    "StudyRoom",
    "StudyRoomMember",
    "UserFavorite",
    "Message",
    "ResourceRequest",
    "ResourceReply",
    "Feedback",
]
