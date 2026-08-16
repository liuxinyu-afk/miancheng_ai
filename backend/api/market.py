"""
资源集市路由
提供资源发布、列表浏览、详情查看、收藏、评分、举报管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.market_resource import MarketResource
from models.resource_extras import ResourceRating, ResourceReport
from models.misc import UserFavorite
from schemas.common import ResponseOK, PageResponse
from schemas.resource import ResourceCreate, ResourceOut
from utils.deps import get_current_user

router = APIRouter(prefix="/api/market", tags=["资源集市"])


# ==================== 评分相关 Schema ====================

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: str = Field(default="", max_length=500, description="评价内容")


class ReportCreate(BaseModel):
    reason: str = Field(..., max_length=50, description="举报原因")
    description: str = Field(default="", max_length=1000, description="详细描述")


@router.post("/publish", response_model=ResponseOK, summary="发布资源")
def publish_resource(
    payload: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发布资源并提交审核，audit_status 默认为 pending"""
    # 教师且已通过实名认证时，标记为认证教师资源
    is_certified = 1 if (
        current_user.role == "teacher" and current_user.cert_status == "approved"
    ) else 0

    # publisher_role 枚举仅允许 student / teacher
    publisher_role = current_user.role if current_user.role in ("student", "teacher") else "student"

    resource = MarketResource(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        attachment_url=payload.attachment_url,
        publisher_id=current_user.id,
        publisher_role=publisher_role,
        is_teacher_certified=is_certified,
        audit_status="pending",
        view_count=0,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    return ResponseOK(data=ResourceOut.model_validate(resource).model_dump())


@router.get("/list", response_model=PageResponse[ResourceOut], summary="获取已审核通过的资源列表")
def list_resources(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    category: str | None = Query(None, description="分类筛选"),
    keyword: str | None = Query(None, description="标题关键词搜索"),
    db: Session = Depends(get_db),
):
    """分页获取已审核通过的资源列表，支持分类筛选与标题关键词搜索"""
    query = db.query(MarketResource).filter(MarketResource.audit_status == "approved")
    if category:
        query = query.filter(MarketResource.category == category)
    if keyword:
        query = query.filter(MarketResource.title.like(f"%{keyword}%"))

    total = query.count()
    resources = (
        query.order_by(MarketResource.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PageResponse[ResourceOut](
        data=[ResourceOut.model_validate(r) for r in resources],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/my-publishments", response_model=ResponseOK, summary="获取我发布的资源列表")
def my_publishments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户发布的所有资源（含所有审核状态）"""
    resources = (
        db.query(MarketResource)
        .filter(MarketResource.publisher_id == current_user.id)
        .order_by(MarketResource.created_at.desc())
        .all()
    )
    return ResponseOK(
        data=[ResourceOut.model_validate(r).model_dump() for r in resources]
    )


@router.get("/my-favorites", response_model=ResponseOK, summary="获取我的收藏列表")
def my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的收藏资源列表"""
    favs = (
        db.query(UserFavorite)
        .filter(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.created_at.desc())
        .all()
    )
    resource_ids = [f.resource_id for f in favs]
    if not resource_ids:
        return ResponseOK(data=[])

    resources = (
        db.query(MarketResource)
        .filter(MarketResource.id.in_(resource_ids))
        .all()
    )
    return ResponseOK(
        data=[ResourceOut.model_validate(r).model_dump() for r in resources]
    )


@router.get("/{resource_id}", response_model=ResourceOut, summary="获取资源详情")
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """获取资源详情，浏览数 +1"""
    resource = db.query(MarketResource).filter(MarketResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 浏览数 +1
    resource.view_count = (resource.view_count or 0) + 1
    db.commit()
    db.refresh(resource)

    return resource


@router.post("/{resource_id}/favorite", response_model=ResponseOK, summary="收藏资源")
def add_favorite(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏指定资源（重复收藏幂等返回）"""
    resource = db.query(MarketResource).filter(MarketResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 检查是否已收藏
    existing = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.resource_id == resource_id,
        )
        .first()
    )
    if existing:
        return ResponseOK(message="已收藏，无需重复操作")

    fav = UserFavorite(user_id=current_user.id, resource_id=resource_id)
    db.add(fav)
    db.commit()

    return ResponseOK(message="收藏成功")


@router.delete("/{resource_id}/favorite", response_model=ResponseOK, summary="取消收藏")
def remove_favorite(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消收藏指定资源"""
    fav = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.resource_id == resource_id,
        )
        .first()
    )
    if not fav:
        raise HTTPException(status_code=404, detail="未找到收藏记录")

    db.delete(fav)
    db.commit()

    return ResponseOK(message="取消收藏成功")


# ==================== 评分相关 ====================

@router.post("/{resource_id}/rate", response_model=ResponseOK, summary="给资源评分")
def rate_resource(
    resource_id: int,
    payload: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """给资源评分（每人每资源仅一次，重复则更新）"""
    resource = db.query(MarketResource).filter(MarketResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    existing = (
        db.query(ResourceRating)
        .filter(ResourceRating.resource_id == resource_id, ResourceRating.user_id == current_user.id)
        .first()
    )
    if existing:
        existing.score = payload.score
        existing.comment = payload.comment
    else:
        rating = ResourceRating(
            resource_id=resource_id,
            user_id=current_user.id,
            score=payload.score,
            comment=payload.comment,
        )
        db.add(rating)
    db.commit()

    # 返回平均分
    avg_score = (
        db.query(func.avg(ResourceRating.score))
        .filter(ResourceRating.resource_id == resource_id)
        .scalar()
    ) or 0
    count = (
        db.query(func.count(ResourceRating.id))
        .filter(ResourceRating.resource_id == resource_id)
        .scalar()
    ) or 0
    return ResponseOK(data={"avg_score": round(float(avg_score), 1), "count": count})


@router.get("/{resource_id}/ratings", response_model=ResponseOK, summary="获取资源评分列表")
def get_ratings(
    resource_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取资源评分列表"""
    query = db.query(ResourceRating).filter(ResourceRating.resource_id == resource_id)
    total = query.count()
    ratings = query.order_by(ResourceRating.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    result = []
    for r in ratings:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "id": r.id,
            "score": r.score,
            "comment": r.comment,
            "created_at": r.created_at,
            "user_name": (user.nickname or user.username) if user else "匿名用户",
            "user_avatar": user.avatar if user else None,
            "user_role": user.role if user else None,
        })

    avg_score = (
        db.query(func.avg(ResourceRating.score))
        .filter(ResourceRating.resource_id == resource_id)
        .scalar()
    ) or 0

    return ResponseOK(data={"ratings": result, "avg_score": round(float(avg_score), 1), "total": total})


# ==================== 举报相关 ====================

@router.post("/{resource_id}/report", response_model=ResponseOK, summary="举报资源")
def report_resource(
    resource_id: int,
    payload: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """举报资源"""
    resource = db.query(MarketResource).filter(MarketResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    report = ResourceReport(
        resource_id=resource_id,
        reporter_id=current_user.id,
        reason=payload.reason,
        description=payload.description,
    )
    db.add(report)
    db.commit()
    return ResponseOK(message="举报已提交，管理员会尽快处理")
