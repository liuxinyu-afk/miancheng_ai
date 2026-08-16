"""审核相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class AuditAction(BaseModel):
    """审核操作请求"""
    content_id: int | None = Field(None, description="被审核内容ID")
    content_type: str | None = Field(None, description="内容类型: resource/achievement/task_package")
    id: int | None = Field(None, description="被审核内容ID（别名）")
    type: str | None = Field(None, description="内容类型（别名）")
    action: str = Field(..., description="审核操作: approve/reject")
    reject_reason: str | None = Field(None, max_length=500, description="驳回理由(reject时必填)")
    reason: str | None = Field(None, max_length=500, description="驳回理由（别名）")


class AuditLogOut(BaseModel):
    id: int
    auditor_id: int
    content_id: int
    content_type: str
    action: str
    reject_reason: str | None = None
    audit_time: datetime

    model_config = {"from_attributes": True}
