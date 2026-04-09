import json
from datetime import datetime
from uuid import uuid4

from app.core.errors import AppError
from app.models.models import Agent, Memory, MemoryState, MemoryType, Persona, Task, TaskStatus
from app.services.audit import AuditService
from app.services.policy import PolicyService
from app.services.provider import OllamaProvider, ProviderUnavailableError


class TaskOrchestrator:
    def run(self, db, task: Task, actor: str) -> Task:
        AuditService.append(
            db,
            trace_id=task.trace_id,
            actor=actor,
            action="task_started",
            resource_type="task",
            resource_id=task.id,
            result=TaskStatus.RUNNING.value,
            request_summary=task.input_text[:200],
        )

        pre = PolicyService.evaluate(task.input_text, "pre_task")
        if pre.decision == "block":
            task.status = TaskStatus.BLOCKED.value
            task.error_text = pre.message
            task.completed_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)
            AuditService.append(
                db,
                trace_id=task.trace_id,
                actor=actor,
                action="task_blocked",
                resource_type="task",
                resource_id=task.id,
                result=TaskStatus.BLOCKED.value,
                request_summary=task.input_text[:200],
                policy_hits=pre.hits,
            )
            return task

        task.status = TaskStatus.RUNNING.value
        db.add(task)
        db.commit()
        db.refresh(task)

        persona = (
            db.query(Persona)
            .filter(Persona.avatar_id == task.avatar_id, Persona.is_current.is_(True))
            .order_by(Persona.created_at.desc())
            .first()
        )
        agent = db.get(Agent, task.agent_id)
        if agent and agent.status == "disabled":
            task.status = TaskStatus.FAILED.value
            task.error_text = "Agent is disabled"
            task.completed_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)
            AuditService.append(
                db,
                trace_id=task.trace_id,
                actor=actor,
                action="task_failed",
                resource_type="task",
                resource_id=task.id,
                result=TaskStatus.FAILED.value,
                request_summary=task.input_text[:200],
            )
            return task

        context = "\n".join(
            [
                "You are the Digital Avatar assistant.",
                persona.summary if persona else "No persona yet.",
                agent.role_prompt if agent else "No agent prompt.",
                task.input_text,
            ]
        )

        try:
            response = OllamaProvider().chat(context)
        except ProviderUnavailableError as exc:
            task.status = TaskStatus.FAILED.value
            task.error_text = str(exc)
            task.completed_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)
            AuditService.append(
                db,
                trace_id=task.trace_id,
                actor=actor,
                action="task_failed",
                resource_type="task",
                resource_id=task.id,
                result=TaskStatus.FAILED.value,
                request_summary=task.input_text[:200],
            )
            return task
        except AppError as exc:
            task.status = TaskStatus.FAILED.value
            task.error_text = exc.message
            task.completed_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)
            AuditService.append(
                db,
                trace_id=task.trace_id,
                actor=actor,
                action="task_failed",
                resource_type="task",
                resource_id=task.id,
                result=TaskStatus.FAILED.value,
                request_summary=task.input_text[:200],
            )
            return task

        post = PolicyService.evaluate(response, "post_provider_output")
        if post.decision == "block":
            task.status = TaskStatus.BLOCKED.value
            task.error_text = post.message
        else:
            task.status = TaskStatus.SUCCEEDED.value
            task.result_text = response
            memory = Memory(
                avatar_id=task.avatar_id,
                task_id=task.id,
                type=MemoryType.EPISODIC.value,
                sensitivity="normal",
                state=MemoryState.PENDING_CONFIRM.value,
                content=response[:240],
                source_type="task",
                source_ref_id=task.id,
            )
            db.add(memory)
            db.flush()
            AuditService.append(
                db,
                trace_id=task.trace_id,
                actor=actor,
                action="memory_captured",
                resource_type="memory",
                resource_id=memory.id,
                result=MemoryState.PENDING_CONFIRM.value,
                request_summary=task.input_text[:200],
            )

        task.completed_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)

        AuditService.append(
            db,
            trace_id=task.trace_id,
            actor=actor,
            action="task_completed" if task.status == TaskStatus.SUCCEEDED.value else "task_blocked",
            resource_type="task",
            resource_id=task.id,
            result=task.status,
            request_summary=task.input_text[:200],
            policy_hits=post.hits,
        )
        return task

    @staticmethod
    def create_task(db, avatar_id: str, agent_id: str, input_text: str, trace_id: str | None = None) -> Task:
        task = Task(
            avatar_id=avatar_id,
            agent_id=agent_id,
            input_text=input_text,
            trace_id=trace_id or uuid4().hex,
            status=TaskStatus.PENDING.value,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
