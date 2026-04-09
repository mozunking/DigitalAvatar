from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Avatar, Memory, User
from app.schemas.common import MemoryDecisionRequest, MemoryResponse, PaginatedResponse
from app.services.audit import AuditService
from app.services.memories import MemoryService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def list_memories(
    avatar_id: str | None = Query(default=None),
    state: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    query = db.query(Memory).join(Avatar, Avatar.id == Memory.avatar_id).filter(Avatar.user_id == current_user.id)
    if avatar_id:
        query = query.filter(Memory.avatar_id == avatar_id)
    if state:
        query = query.filter(Memory.state == state)
    total = query.count()
    items = query.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[MemoryResponse.model_validate(item).model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryResponse:
    memory = db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    avatar = db.get(Avatar, memory.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse.model_validate(memory)


@router.post("/{memory_id}/confirm", response_model=MemoryResponse)
def confirm_memory(
    memory_id: str,
    payload: MemoryDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryResponse:
    memory = db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    avatar = db.get(Avatar, memory.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Memory not found")
    result = MemoryService.confirm(db, memory)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="memory_confirmed",
        resource_type="memory",
        resource_id=memory.id,
        result="confirmed",
        request_summary=f"type={memory.type};reason={payload.reason or 'N/A'}",
    )
    return MemoryResponse.model_validate(result)


@router.post("/{memory_id}/reject", response_model=MemoryResponse)
def reject_memory(
    memory_id: str,
    payload: MemoryDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryResponse:
    memory = db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    avatar = db.get(Avatar, memory.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Memory not found")
    result = MemoryService.reject(db, memory)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="memory_rejected",
        resource_type="memory",
        resource_id=memory.id,
        result="rejected",
        request_summary=f"type={memory.type};reason={payload.reason or 'N/A'}",
    )
    return MemoryResponse.model_validate(result)


@router.post("/{memory_id}/archive", response_model=MemoryResponse, status_code=status.HTTP_200_OK)
def archive_memory(
    memory_id: str,
    payload: MemoryDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryResponse:
    memory = db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    avatar = db.get(Avatar, memory.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Memory not found")
    result = MemoryService.archive(db, memory)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="memory_archived",
        resource_type="memory",
        resource_id=memory.id,
        result="archived",
        request_summary=f"reason={payload.reason or 'N/A'}",
    )
    return MemoryResponse.model_validate(result)
