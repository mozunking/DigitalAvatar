import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import AuditLog, User
from app.schemas.common import AuditLogResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def list_audit_logs(
    trace_id: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    query = db.query(AuditLog)
    if trace_id:
        query = query.filter(AuditLog.trace_id == trace_id)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_at:
        query = query.filter(AuditLog.created_at >= start_at)
    if end_at:
        query = query.filter(AuditLog.created_at <= end_at)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[AuditLogResponse.model_validate(item).model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{audit_id}", response_model=AuditLogResponse)
def get_audit_log(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuditLogResponse:
    item = db.get(AuditLog, audit_id)
    if not item:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return AuditLogResponse.model_validate(item)
