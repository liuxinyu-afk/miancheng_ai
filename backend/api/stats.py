"""
公开统计路由
所有登录用户均可访问，提供平台概览数据。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.market_resource import MarketResource
from models.task_package import TaskPackage
from models.achievement import AchievementPost
from schemas.common import ResponseOK
from utils.deps import get_current_user

router = APIRouter(
    prefix="/api/stats",
    tags=["数据统计"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/overview", summary="平台概览统计（所有登录用户可访问）")
def get_overview(db: Session = Depends(get_db)):
    """返回平台基本统计数据，供仪表盘展示"""
    total_users = db.query(User).count()
    total_resources = db.query(MarketResource).count()
    total_tasks = db.query(TaskPackage).count()
    total_achievements = db.query(AchievementPost).count()

    # 各角色用户数
    role_counts = {}
    for role in ("student", "teacher", "auditor", "admin"):
        role_counts[role] = db.query(User).filter(User.role == role).count()

    data = {
        "user_count": total_users,
        "resource_count": total_resources,
        "task_count": total_tasks,
        "post_count": total_achievements,
        "role_distribution": role_counts,
    }
    return ResponseOK(data=data)
