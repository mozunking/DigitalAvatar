from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Avatar, Memory, User
from app.schemas.common import MemoryPageResponse, MemoryResponse, MemorySummaryPageResponse, MemorySummaryResponse

router = APIRouter()


@router.get("/{avatar_id}/memories/search", response_model=MemorySummaryPageResponse)
def search_memories(
    avatar_id: str,
    query_str: str | None = Query(default=None, alias="query"),
    type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemorySummaryPageResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Avatar not found")
    q = db.query(Memory).filter(Memory.avatar_id == avatar_id, Memory.state == "confirmed")
    if type:
        q = q.filter(Memory.type == type)
    if query_str:
        q = q.filter(Memory.content.ilike(f"%{query_str}%"))
    total = q.count()
    items = q.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return MemorySummaryPageResponse(
        items=[MemorySummaryResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{avatar_id}/memories/pending", response_model=MemoryPageResponse)
def list_pending_memories(
    avatar_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryPageResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Avatar not found")
    q = db.query(Memory).filter(Memory.avatar_id == avatar_id, Memory.state == "pending_confirm")
    total = q.count()
    items = q.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return MemoryPageResponse(
        items=[MemoryResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{avatar_id}/memories/{memory_id}", response_model=MemoryResponse)
def get_avatar_memory(
    avatar_id: str,
    memory_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemoryResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Avatar not found")
    memory = db.get(Memory, memory_id)
    if not memory or memory.avatar_id != avatar_id:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse.model_validate(memory)
