import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Agent, Avatar, User
from app.schemas.common import AgentResponse, CreateAgentRequest, PaginatedResponse, UpdateAgentStatusRequest
from app.services.audit import AuditService

router = APIRouter()


@router.post("/{avatar_id}/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    avatar_id: str,
    payload: CreateAgentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    agent = Agent(
        avatar_id=avatar_id,
        name=payload.name,
        role_prompt=payload.role_prompt,
        permissions=json.dumps(payload.permissions),
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action="agent_created",
        resource_type="agent",
        resource_id=agent.id,
        result="success",
        request_summary=f"avatar={avatar_id};name={payload.name}",
    )
    return AgentResponse.model_validate(agent)


@router.get("/{avatar_id}/agents", response_model=PaginatedResponse)
def list_agents(
    avatar_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    avatar = db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    query = db.query(Agent).filter(Agent.avatar_id == avatar_id).order_by(Agent.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[AgentResponse.model_validate(item).model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{avatar_id}/agents/{agent_id}", response_model=AgentResponse)
def get_agent(
    avatar_id: str,
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentResponse:
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    avatar = db.get(Avatar, agent.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.patch("/{avatar_id}/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    avatar_id: str,
    agent_id: str,
    payload: UpdateAgentStatusRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentResponse:
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    avatar = db.get(Avatar, agent.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if payload.status not in {"ready", "disabled"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported agent status")
    agent.status = payload.status
    db.add(agent)
    db.commit()
    db.refresh(agent)
    AuditService.append(
        db,
        trace_id=getattr(request.state, "trace_id", "-"),
        actor=current_user.email,
        action=f"agent_{payload.status}",
        resource_type="agent",
        resource_id=agent.id,
        result=payload.status,
        request_summary=f"avatar={avatar_id};status={payload.status}",
    )
    return AgentResponse.model_validate(agent)
