from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Avatar, User
from app.schemas.common import AvatarResponse, CreateAvatarRequest, PaginatedResponse, UpdateAvatarRequest
from app.services.audit import AuditService

router = APIRouter()


@router.post("", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
def create_avatar(
    payload: CreateAvatarRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvatarResponse:
    avatar = Avatar(user_id=current_user.id, name=payload.name, goal=payload.goal, visibility=payload.visibility)
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="avatar_created",
        resource_type="avatar",
        resource_id=avatar.id,
        result="success",
        request_summary=f"name={payload.name}",
    )
    return AvatarResponse.model_validate(avatar)


@router.get("", response_model=PaginatedResponse)
def list_avatars(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    query = db.query(Avatar).filter(Avatar.user_id == current_user.id).order_by(Avatar.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[AvatarResponse.model_validate(item).model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.patch("/{avatar_id}", response_model=AvatarResponse)
def update_avatar(
    avatar_id: str,
    payload: UpdateAvatarRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvatarResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    avatar.name = payload.name
    avatar.goal = payload.goal
    avatar.visibility = payload.visibility
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    return AvatarResponse.model_validate(avatar)


@router.get("/{avatar_id}", response_model=AvatarResponse)
def get_avatar(
    avatar_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvatarResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return AvatarResponse.model_validate(avatar)
