from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.v1 import agents, audit, auth, avatar_memories, memories, persona_activate, personas, tasks
from app.api.v1 import avatars as avatars_mod
from app.core.deps import get_current_user, get_db
from app.models.models import Agent, AuditLog, Avatar, Memory, Persona, Task, User
from app.services.provider import OllamaProvider

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Avatar CRUD
router.include_router(avatars_mod.router, prefix="/avatars", tags=["avatars"])

# Nested resources under /avatars/{avatar_id}
router.include_router(personas.router, prefix="/avatars", tags=["personas"])
router.include_router(agents.router, prefix="/avatars", tags=["agents"])
router.include_router(avatar_memories.router, prefix="/avatars", tags=["memories"])

# Top-level resources
router.include_router(persona_activate.router, prefix="/personas", tags=["personas"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(memories.router, prefix="/memories", tags=["memories"])
router.include_router(audit.router, prefix="/audit", tags=["audit"])

provider_router = APIRouter(prefix="/provider", tags=["provider"])

@provider_router.get("/health")
def provider_health():
    provider = OllamaProvider()
    return provider.health_check()

router.include_router(provider_router)

privacy_router = APIRouter(prefix="/privacy", tags=["privacy"])


@privacy_router.get("/export")
def export_privacy_data(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    avatars = db.query(Avatar).filter(Avatar.user_id == current_user.id).all()
    avatar_ids = [a.id for a in avatars]
    persona_ids = [item[0] for item in db.query(Persona.id).filter(Persona.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    agent_ids = [item[0] for item in db.query(Agent.id).filter(Agent.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    task_ids = [item[0] for item in db.query(Task.id).filter(Task.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    memories = db.query(Memory).filter(Memory.avatar_id.in_(avatar_ids)).all() if avatar_ids else []
    tasks = db.query(Task).filter(Task.avatar_id.in_(avatar_ids)).all() if avatar_ids else []
    personas = db.query(Persona).filter(Persona.avatar_id.in_(avatar_ids)).all() if avatar_ids else []
    agents_list = db.query(Agent).filter(Agent.avatar_id.in_(avatar_ids)).all() if avatar_ids else []
    audits = (
        db.query(AuditLog)
        .filter(
            (AuditLog.actor == current_user.email)
            | ((AuditLog.resource_type == "avatar") & (AuditLog.resource_id.in_(avatar_ids)))
            | ((AuditLog.resource_type == "persona") & (AuditLog.resource_id.in_(persona_ids)))
            | ((AuditLog.resource_type == "agent") & (AuditLog.resource_id.in_(agent_ids)))
            | ((AuditLog.resource_type == "task") & (AuditLog.resource_id.in_(task_ids)))
            | ((AuditLog.resource_type == "memory") & (AuditLog.resource_id.in_([m.id for m in memories])))
        )
        .all()
        if avatar_ids
        else db.query(AuditLog).filter(AuditLog.actor == current_user.email).all()
    )

    return {
        "user": {"id": current_user.id, "email": current_user.email, "display_name": current_user.display_name},
        "avatars": [{"id": a.id, "name": a.name, "goal": a.goal, "created_at": a.created_at.isoformat()} for a in avatars],
        "personas": [{"id": p.id, "avatar_id": p.avatar_id, "version": p.version, "is_current": p.is_current, "created_at": p.created_at.isoformat()} for p in personas],
        "agents": [{"id": a.id, "avatar_id": a.avatar_id, "name": a.name, "status": a.status, "created_at": a.created_at.isoformat()} for a in agents_list],
        "memories": [{"id": m.id, "content": m.content, "state": m.state, "type": m.type, "created_at": m.created_at.isoformat()} for m in memories],
        "tasks": [{"id": t.id, "input": t.input_text, "result": t.result_text, "status": t.status, "created_at": t.created_at.isoformat()} for t in tasks],
        "audit_logs": [{"id": a.id, "trace_id": a.trace_id, "action": a.action, "resource_type": a.resource_type, "resource_id": a.resource_id, "created_at": a.created_at.isoformat()} for a in audits],
        "exported_at": datetime.utcnow().isoformat(),
    }


@privacy_router.delete("/delete")
def delete_privacy_data(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    avatar_ids = [a.id for a in db.query(Avatar).filter(Avatar.user_id == current_user.id).all()]
    persona_ids = [item[0] for item in db.query(Persona.id).filter(Persona.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    agent_ids = [item[0] for item in db.query(Agent.id).filter(Agent.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    task_ids = [item[0] for item in db.query(Task.id).filter(Task.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []
    memory_ids = [item[0] for item in db.query(Memory.id).filter(Memory.avatar_id.in_(avatar_ids)).all()] if avatar_ids else []

    audit_query = db.query(AuditLog).filter(AuditLog.actor == current_user.email)
    if avatar_ids:
        audit_query = audit_query.union(
            db.query(AuditLog).filter(AuditLog.resource_type == "avatar", AuditLog.resource_id.in_(avatar_ids)),
            db.query(AuditLog).filter(AuditLog.resource_type == "persona", AuditLog.resource_id.in_(persona_ids)),
            db.query(AuditLog).filter(AuditLog.resource_type == "agent", AuditLog.resource_id.in_(agent_ids)),
            db.query(AuditLog).filter(AuditLog.resource_type == "task", AuditLog.resource_id.in_(task_ids)),
            db.query(AuditLog).filter(AuditLog.resource_type == "memory", AuditLog.resource_id.in_(memory_ids)),
        )
    audit_ids = [item.id for item in audit_query.all()]
    if audit_ids:
        db.query(AuditLog).filter(AuditLog.id.in_(audit_ids)).delete(synchronize_session=False)
    if avatar_ids:
        db.query(Memory).filter(Memory.avatar_id.in_(avatar_ids)).delete(synchronize_session=False)
        db.query(Task).filter(Task.avatar_id.in_(avatar_ids)).delete(synchronize_session=False)
        db.query(Persona).filter(Persona.avatar_id.in_(avatar_ids)).delete(synchronize_session=False)
        db.query(Agent).filter(Agent.avatar_id.in_(avatar_ids)).delete(synchronize_session=False)
        db.query(Avatar).filter(Avatar.user_id == current_user.id).delete(synchronize_session=False)
    db.query(User).filter(User.id == current_user.id).delete(synchronize_session=False)
    db.commit()
    return {"status": "deleted", "message": "All user data has been permanently deleted"}


router.include_router(privacy_router)
