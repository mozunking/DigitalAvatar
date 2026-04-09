from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Task
from app.services.tasks import TaskOrchestrator


def run_task(task_id: str, actor: str) -> None:
    with SessionLocal() as db:
        task = db.get(Task, task_id)
        if not task:
            return
        TaskOrchestrator().run(db, task, actor)
