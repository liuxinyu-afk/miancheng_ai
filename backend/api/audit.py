"""
审核管理路由
审核员/管理员可对待审核内容(资源、成果帖子、任务包)进行审核操作，
所有接口均需要审核员或管理员权限。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.market_resource import MarketResource
from models.achievement import AchievementPost
from models.task_package import TaskPackage
from models.audit_log import AuditLog
from models.misc import Message
from models.user import User
from schemas.common import ResponseOK, PageResponse
from schemas.audit import AuditAction, AuditLogOut
from utils.deps import get_current_user, require_auditor

router = APIRouter(
    prefix="/api/audit",
    tags=["审核管理"],
    dependencies=[Depends(require_auditor)],
)

# 内容类型与对应 ORM 模型的映射
_CONTENT_TYPE_MODELS = {
    "resource": MarketResource,
    "achievement": AchievementPost,
    "task_package": TaskPackage,
}

# 内容类型对应的中文描述，用于站内消息文案
_CONTENT_TYPE_LABEL = {
    "resource": "学习资源",
    "achievement": "成果帖子",
    "task_package": "任务包",
}


def _build_pending_item(record, content_type: str, submitter: User | None = None) -> dict:
    """将不同模型的待审核记录统一为标准输出格式"""
    submitter_name = None
    submitter_role = None
    if submitter:
        submitter_name = submitter.nickname or submitter.username
        submitter_role = submitter.role

    if content_type == "resource":
        return {
            "id": record.id,
            "type": content_type,
            "title": record.title,
            "preview": (record.content or "")[:100],
            "user_id": record.publisher_id,
            "username": submitter_name,
            "role": submitter_role,
            "created_at": record.created_at,
        }
    if content_type == "achievement":
        text = record.content or ""
        return {
            "id": record.id,
            "type": content_type,
            "title": text[:50],
            "preview": text[:100],
            "user_id": record.user_id,
            "username": submitter_name,
            "role": submitter_role,
            "created_at": record.created_at,
        }
    # task_package
    return {
        "id": record.id,
        "type": content_type,
        "title": record.title,
        "preview": (record.description or "")[:100],
        "user_id": record.publisher_id,
        "username": submitter_name,
        "role": submitter_role,
        "created_at": record.created_at,
    }


@router.get("/pending", summary="获取待审核内容列表")
def get_pending_list(
    content_type: str | None = Query(
        None, description="内容类型筛选: resource/achievement/task_package"
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    # 校验内容类型参数
    if content_type and content_type not in _CONTENT_TYPE_MODELS:
        raise HTTPException(
            status_code=400,
            detail="content_type 取值须为 resource/achievement/task_package",
        )

    # 确定需要查询的内容类型集合：指定了则只查该类型，否则查全部
    types_to_query = [content_type] if content_type else list(_CONTENT_TYPE_MODELS.keys())

    # 分别查询各类待审核记录并合并为统一格式
    items: list[dict] = []
    for ctype in types_to_query:
        model = _CONTENT_TYPE_MODELS[ctype]
        records = db.query(model).filter(model.audit_status == "pending").all()
        for record in records:
            # 查询提交人信息
            submitter_id = None
            if ctype == "achievement":
                submitter_id = record.user_id
            else:
                submitter_id = record.publisher_id
            submitter = None
            if submitter_id:
                submitter = db.query(User).filter(User.id == submitter_id).first()
            items.append(_build_pending_item(record, ctype, submitter))

    # 按创建时间倒序排序（created_at 为 None 时排到最后）
    items.sort(key=lambda x: x["created_at"] or datetime.min, reverse=True)

    # 内存分页
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]

    return PageResponse(data=page_items, total=total, page=page, page_size=page_size)


@router.get("/pending/{content_type}/{content_id}", summary="获取待审核内容详情预览")
def get_pending_detail(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
):
    if content_type not in _CONTENT_TYPE_MODELS:
        raise HTTPException(
            status_code=400,
            detail="content_type 取值须为 resource/achievement/task_package",
        )

    model = _CONTENT_TYPE_MODELS[content_type]
    record = (
        db.query(model)
        .filter(model.id == content_id, model.audit_status == "pending")
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="待审核内容不存在或已被审核")

    # 查询提交人信息
    submitter_id = record.user_id if content_type == "achievement" else record.publisher_id
    submitter = None
    if submitter_id:
        submitter = db.query(User).filter(User.id == submitter_id).first()

    # 基础统一信息
    base = _build_pending_item(record, content_type, submitter)

    # 附加各类型的完整内容字段，供审核员预览
    if content_type == "resource":
        base.update(
            {
                "category": record.category,
                "content": record.content,
                "attachment_url": record.attachment_url,
                "publisher_role": record.publisher_role,
                "is_teacher_certified": record.is_teacher_certified,
            }
        )
    elif content_type == "achievement":
        base.update(
            {
                "content": record.content,
                "images": record.images,
                "like_count": record.like_count,
                "comment_count": record.comment_count,
            }
        )
    else:  # task_package
        base.update(
            {
                "category": record.category,
                "source": record.source,
                "description": record.description,
                "daily_hours": record.daily_hours,
                "level": record.level,
                "is_official": record.is_official,
            }
        )

    return ResponseOK(data=base)


@router.post("/review", summary="审核操作")
def review_content(
    body: AuditAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 兼容前端两种字段名
    content_type = body.content_type or body.type
    content_id = body.content_id or body.id
    reject_reason = body.reject_reason or body.reason

    # 校验内容类型
    if content_type not in _CONTENT_TYPE_MODELS:
        raise HTTPException(
            status_code=400,
            detail="content_type 取值须为 resource/achievement/task_package",
        )
    # 校验操作类型
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="action 取值须为 approve/reject")
    # 驳回操作必须填写驳回理由
    if body.action == "reject" and not reject_reason:
        raise HTTPException(status_code=400, detail="驳回操作须填写驳回理由")

    model = _CONTENT_TYPE_MODELS[content_type]
    record = db.query(model).filter(model.id == content_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="被审核内容不存在")

    # 确定发布人ID及内容标题（用于站内消息通知）
    if content_type == "achievement":
        publisher_id = record.user_id
        content_title = (record.content or "")[:50]
    elif content_type == "resource":
        publisher_id = record.publisher_id
        content_title = record.title
    else:  # task_package
        publisher_id = record.publisher_id
        content_title = record.title

    type_label = _CONTENT_TYPE_LABEL[content_type]

    # 更新对应表的审核状态
    if body.action == "approve":
        record.audit_status = "approved"
        record.reject_reason = None
        msg_title = "审核通过"
        msg_content = f"您发布的{type_label}《{content_title}》已审核通过。"
    else:
        record.audit_status = "rejected"
        record.reject_reason = reject_reason
        msg_title = "审核驳回"
        msg_content = (
            f"您发布的{type_label}《{content_title}》被驳回，理由：{reject_reason}"
        )

    # 创建审核记录
    audit_log = AuditLog(
        auditor_id=current_user.id,
        content_id=content_id,
        content_type=content_type,
        action=body.action,
        reject_reason=reject_reason,
    )
    db.add(audit_log)

    # 创建站内消息通知发布人
    if publisher_id is not None:
        message = Message(
            user_id=publisher_id,
            title=msg_title,
            content=msg_content,
            msg_type="audit",
            is_read=0,
        )
        db.add(message)

    db.commit()

    return ResponseOK(
        data={
            "content_id": content_id,
            "content_type": content_type,
            "audit_status": record.audit_status,
        }
    )


@router.get("/history", summary="获取当前审核员的历史审核记录")
def get_audit_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 查询当前审核员操作过的审核记录
    query = db.query(AuditLog).filter(AuditLog.auditor_id == current_user.id)
    total = query.count()
    records = (
        query.order_by(AuditLog.audit_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [AuditLogOut.model_validate(r) for r in records]
    return PageResponse(data=data, total=total, page=page, page_size=page_size)
