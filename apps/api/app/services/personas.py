import json
from datetime import datetime

from app.models.models import Memory, MemoryState, MemoryType, Persona
from app.services.policy import PolicyService
from app.services.provider import OllamaProvider


class PersonaService:
    def generate(self, db, avatar_id: str, samples: list[str]) -> Persona:
        db.query(Persona).filter(Persona.avatar_id == avatar_id, Persona.is_current.is_(True)).update(
            {Persona.is_current: False}
        )
        summary = OllamaProvider().chat("\n".join(["Generate persona summary", *samples]))[:1000]
        latest = db.query(Persona).filter(Persona.avatar_id == avatar_id).order_by(Persona.version.desc()).first()
        persona = Persona(
            avatar_id=avatar_id,
            summary=summary,
            source_count=len(samples),
            version=(latest.version + 1) if latest else 1,
            is_current=True,
        )
        db.add(persona)
        db.add(
            Memory(
                avatar_id=avatar_id,
                task_id=None,
                type=MemoryType.PROFILE.value,
                sensitivity="normal",
                state=MemoryState.PENDING_CONFIRM.value,
                content=summary[:240],
                source_type="persona",
                source_ref_id=None,
            )
        )
        db.commit()
        db.refresh(persona)
        return persona

    def activate(self, db, persona: Persona) -> Persona:
        db.query(Persona).filter(Persona.avatar_id == persona.avatar_id, Persona.is_current.is_(True)).update(
            {Persona.is_current: False}
        )
        persona.is_current = True
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona
