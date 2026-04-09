from threading import Thread

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.models import Agent, Avatar, Task, User
from app.schemas.common import CreateTaskRequest, PaginatedResponse, TaskResponse
from app.services.audit import AuditService
from app.services.tasks import TaskOrchestrator
from app.worker import run_task

router = APIRouter()
service = TaskOrchestrator()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: CreateTaskRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    avatar = db.get(Avatar, payload.avatar_id)
    agent = db.get(Agent, payload.agent_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    if not agent or agent.avatar_id != avatar.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    task = service.create_task(db, avatar_id=payload.avatar_id, agent_id=payload.agent_id, input_text=payload.input, trace_id=payload.trace_id)
    trace_id = task.trace_id or getattr(request.state, "trace_id", "-")
    AuditService.append(
        db,
        trace_id=trace_id,
        actor=current_user.email,
        action="task_created",
        resource_type="task",
        resource_id=task.id,
        result=task.status,
        request_summary=f"agent={payload.agent_id}",
    )
    Thread(target=run_task, args=(task.id, current_user.email), daemon=True).start()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.get("", response_model=PaginatedResponse)
def list_tasks(
    avatar_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse:
    query = db.query(Task).join(Avatar, Avatar.id == Task.avatar_id).filter(Avatar.user_id == current_user.id)
    if avatar_id:
        query = query.filter(Task.avatar_id == avatar_id)
    items = query.order_by(Task.created_at.desc()).all()
    return PaginatedResponse(
        items=[TaskResponse.model_validate(item).model_dump(by_alias=True) for item in items],
        total=len(items),
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    avatar = db.get(Avatar, task.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse.model_validate(task)
