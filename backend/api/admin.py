"""
系统管理路由
管理员可查看数据看板、管理用户账号、审核教师认证、创建审核员账号及查看统计数据，
所有接口均需要管理员权限。
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.market_resource import MarketResource
from models.task_package import TaskPackage
from models.achievement import AchievementPost
from models.resource_extras import ResourceReport
from schemas.common import ResponseOK, PageResponse
from schemas.user import UserOut
from utils.deps import get_current_user, require_admin
from utils.security import hash_password

from datetime import datetime, date, timedelta

router = APIRouter(
    prefix="/api/admin",
    tags=["系统管理"],
    dependencies=[Depends(require_admin)],
)


# ---------- 请求体模型 ----------


class UserStatusUpdate(BaseModel):
    """启用/禁用用户账号请求"""
    status: int = Field(..., description="1=启用 0=禁用")


class CertReviewAction(BaseModel):
    """教师认证审核请求"""
    action: str = Field(..., description="审核操作: approve/reject")


class AuditorCreate(BaseModel):
    """创建审核员账号请求"""
    username: str = Field(..., min_length=3, max_length=50, description="登录账号")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")


# ---------- 数据看板 ----------


@router.get("/dashboard", summary="数据看板统计")
def get_dashboard(db: Session = Depends(get_db)):
    # 总用户数
    total_users = db.query(User).count()

    # 各角色用户数
    role_counts = {}
    for role in ("student", "teacher", "auditor", "admin"):
        role_counts[role] = db.query(User).filter(User.role == role).count()

    # 教师认证数（已通过实名认证）
    certified_teachers = db.query(User).filter(User.cert_status == "approved").count()

    # 资源总量
    total_resources = db.query(MarketResource).count()

    # 任务包总量
    total_tasks = db.query(TaskPackage).count()

    # 待审核内容数（三类内容合计）
    pending_resources = (
        db.query(MarketResource).filter(MarketResource.audit_status == "pending").count()
    )
    pending_achievements = (
        db.query(AchievementPost).filter(AchievementPost.audit_status == "pending").count()
    )
    pending_tasks = (
        db.query(TaskPackage).filter(TaskPackage.audit_status == "pending").count()
    )
    pending_total = pending_resources + pending_achievements + pending_tasks

    # 成果帖子总量
    total_achievements = db.query(AchievementPost).count()

    data = {
        "total_users": total_users,
        "role_counts": role_counts,
        "certified_teachers": certified_teachers,
        "total_resources": total_resources,
        "total_tasks": total_tasks,
        "pending_total": pending_total,
        "pending_breakdown": {
            "resource": pending_resources,
            "achievement": pending_achievements,
            "task_package": pending_tasks,
        },
        "total_achievements": total_achievements,
    }
    return ResponseOK(data=data)


# ---------- 用户管理 ----------


@router.get("/users", summary="获取全量用户列表")
def get_users(
    role: str | None = Query(None, description="角色筛选: student/teacher/auditor/admin"),
    keyword: str | None = Query(None, description="搜索 username/nickname"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    # 角色筛选
    if role:
        query = query.filter(User.role == role)

    # 关键词搜索（用户名或昵称模糊匹配）
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((User.username.like(like)) | (User.nickname.like(like)))

    total = query.count()
    records = (
        query.order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [UserOut.model_validate(r) for r in records]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)


@router.put("/users/{user_id}/status", summary="启用/禁用用户账号")
def update_user_status(
    user_id: int,
    body: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.status not in (0, 1):
        raise HTTPException(status_code=400, detail="status 取值须为 0 或 1")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 防止管理员禁用自己的账号导致无法登录
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")

    user.status = body.status
    db.commit()

    return ResponseOK(data={"user_id": user_id, "status": user.status})


# ---------- 教师实名认证审核 ----------


@router.get("/cert-requests", summary="获取待审核的教师实名认证列表")
def get_cert_requests(db: Session = Depends(get_db)):
    # 查询所有处于待审核状态的教师认证申请
    records = db.query(User).filter(User.cert_status == "pending").all()
    data = [
        {
            "user_id": r.id,
            "username": r.username,
            "nickname": r.nickname,
            "real_name": r.real_name,
            "teacher_no": r.teacher_no,
        }
        for r in records
    ]
    return ResponseOK(data=data)


@router.put("/cert-requests/{user_id}", summary="审核教师实名认证")
def review_cert_request(
    user_id: int,
    body: CertReviewAction,
    db: Session = Depends(get_db),
):
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="action 取值须为 approve/reject")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.cert_status != "pending":
        raise HTTPException(status_code=400, detail="该用户当前不在待审核认证状态")

    # approve 设为 approved，reject 设为 rejected
    user.cert_status = "approved" if body.action == "approve" else "rejected"
    db.commit()

    return ResponseOK(data={"user_id": user_id, "cert_status": user.cert_status})


# ---------- 审核员账号管理 ----------


@router.post("/auditors", summary="创建审核员账号")
def create_auditor(body: AuditorCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    exists = db.query(User).filter(User.username == body.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建审核员账号，密码使用 bcrypt 加密
    auditor = User(
        username=body.username,
        password=hash_password(body.password),
        role="auditor",
        nickname=body.nickname,
        cert_status="none",
        status=1,
    )
    db.add(auditor)
    db.commit()
    db.refresh(auditor)

    return ResponseOK(
        data={
            "id": auditor.id,
            "username": auditor.username,
            "nickname": auditor.nickname,
            "role": auditor.role,
        }
    )


# ---------- 数据统计 ----------


@router.get("/stats/resources", summary="资源数据统计(按分类分组计数)")
def stats_resources(db: Session = Depends(get_db)):
    # 按 category 分组统计资源数量
    rows = (
        db.query(MarketResource.category, func.count(MarketResource.id))
        .group_by(MarketResource.category)
        .all()
    )
    by_category = {category: count for category, count in rows}
    total = sum(by_category.values())

    return ResponseOK(data={"by_category": by_category, "total": total})


@router.get("/stats/tasks", summary="任务包数据统计(按分类分组计数及来源占比)")
def stats_tasks(db: Session = Depends(get_db)):
    # 按分类分组计数
    rows = (
        db.query(TaskPackage.category, func.count(TaskPackage.id))
        .group_by(TaskPackage.category)
        .all()
    )
    by_category = {category: count for category, count in rows}
    total = sum(by_category.values())

    # AI生成 vs 用户发布 数量及占比
    ai_count = db.query(TaskPackage).filter(TaskPackage.source == "ai_generated").count()
    user_count = (
        db.query(TaskPackage).filter(TaskPackage.source == "user_published").count()
    )
    source_total = ai_count + user_count
    source = {
        "ai_generated": ai_count,
        "user_published": user_count,
        "ai_generated_ratio": round(ai_count / source_total, 4) if source_total else 0,
        "user_published_ratio": round(user_count / source_total, 4) if source_total else 0,
    }

    return ResponseOK(data={"by_category": by_category, "total": total, "source": source})


# ---------- 趋势数据 ----------


@router.get("/trends", summary="近7天数据趋势")
def get_trends(db: Session = Depends(get_db)):
    """获取近7天注册用户、资源发布、成果帖子、任务包的趋势数据"""
    today = date.today()
    dates = [(today - timedelta(days=6-i)) for i in range(7)]
    date_strs = [d.isoformat() for d in dates]

    def _daily_count(model, date_field):
        result = []
        for d in dates:
            next_d = d + timedelta(days=1)
            count = (
                db.query(model)
                .filter(date_field >= d, date_field < next_d)
                .count()
            )
            result.append(count)
        return result

    user_trend = _daily_count(User, User.created_at)
    resource_trend = _daily_count(MarketResource, MarketResource.created_at)
    achievement_trend = _daily_count(AchievementPost, AchievementPost.created_at)
    task_trend = _daily_count(TaskPackage, TaskPackage.created_at)

    return ResponseOK(data={
        "dates": date_strs,
        "users": user_trend,
        "resources": resource_trend,
        "achievements": achievement_trend,
        "tasks": task_trend,
    })


# ---------- 举报管理 ----------


@router.get("/reports", summary="获取举报列表")
def get_reports(
    status: str = Query("pending", description="状态筛选: pending/resolved/dismissed"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取举报列表"""
    query = db.query(ResourceReport)
    if status:
        query = query.filter(ResourceReport.status == status)

    total = query.count()
    reports = (
        query.order_by(ResourceReport.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for r in reports:
        resource = db.query(MarketResource).filter(MarketResource.id == r.resource_id).first()
        reporter = db.query(User).filter(User.id == r.reporter_id).first()
        result.append({
            "id": r.id,
            "resource_id": r.resource_id,
            "resource_title": resource.title if resource else "已删除",
            "reporter_name": (reporter.nickname or reporter.username) if reporter else "未知",
            "reason": r.reason,
            "description": r.description,
            "status": r.status,
            "created_at": r.created_at,
        })

    return PageResponse(data=result, total=total, page=page, page_size=page_size)


class ReportAction(BaseModel):
    action: str = Field(..., description="resolve=处理/dismiss=驳回")


@router.put("/reports/{report_id}", summary="处理举报")
def handle_report(
    report_id: int,
    body: ReportAction,
    db: Session = Depends(get_db),
):
    if body.action not in ("resolve", "dismiss"):
        raise HTTPException(status_code=400, detail="action 取值须为 resolve/dismiss")

    report = db.query(ResourceReport).filter(ResourceReport.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    report.status = "resolved" if body.action == "resolve" else "dismissed"
    db.commit()
    return ResponseOK(message="举报已处理")
