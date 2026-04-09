from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Avatar, Persona, User
from app.schemas.common import PaginatedResponse, PersonaGenerateRequest, PersonaResponse
from app.services.audit import AuditService
from app.services.personas import PersonaService

router = APIRouter()
service = PersonaService()


@router.post("/{avatar_id}/persona/generate", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
def generate_persona(
    avatar_id: str,
    payload: PersonaGenerateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    persona = service.generate(db, avatar_id=avatar.id, samples=payload.samples)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="persona_generated",
        resource_type="persona",
        resource_id=persona.id,
        result="success",
        request_summary=f"avatar={avatar_id};version={persona.version};samples={len(payload.samples)}",
    )
    return PersonaResponse.model_validate(persona)


@router.get("/{avatar_id}/personas", response_model=PaginatedResponse)
def list_personas(
    avatar_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    query = db.query(Persona).filter(Persona.avatar_id == avatar_id).order_by(Persona.version.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[PersonaResponse.model_validate(item).model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{avatar_id}/persona/latest", response_model=PersonaResponse)
def latest_persona(
    avatar_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    persona = (
        db.query(Persona)
        .filter(Persona.avatar_id == avatar_id, Persona.is_current.is_(True))
        .order_by(Persona.created_at.desc())
        .first()
    )
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return PersonaResponse.model_validate(persona)
