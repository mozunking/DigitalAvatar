from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Avatar, Persona, User
from app.schemas.common import PersonaResponse
from app.services.audit import AuditService
from app.services.personas import PersonaService

router = APIRouter()
service = PersonaService()


@router.post("/{persona_id}/activate", response_model=PersonaResponse)
def activate_persona(
    persona_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PersonaResponse:
    persona = db.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    avatar = db.get(Avatar, persona.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    result = service.activate(db, persona)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="persona_activated",
        resource_type="persona",
        resource_id=persona.id,
        result="activated",
        request_summary=f"avatar={persona.avatar_id};version={persona.version}",
    )
    return PersonaResponse.model_validate(result)
