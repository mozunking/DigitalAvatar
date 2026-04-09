from fastapi import status

from app.core.errors import AppError
from app.models.models import Memory, MemoryState
from app.services.policy import PolicyService


class MemoryService:
    @staticmethod
    def confirm(db, memory: Memory) -> Memory:
        if memory.state != MemoryState.PENDING_CONFIRM.value:
            raise AppError(
                code="MEMORY_STATE_CONFLICT",
                message="Memory is not pending confirmation",
                status_code=status.HTTP_409_CONFLICT,
                details={"state": memory.state},
            )
        decision = PolicyService.evaluate(memory.content, "pre_memory_write")
        if decision.decision == "block":
            memory.state = MemoryState.REJECTED.value
        else:
            memory.state = MemoryState.CONFIRMED.value
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def reject(db, memory: Memory) -> Memory:
        if memory.state != MemoryState.PENDING_CONFIRM.value:
            raise AppError(
                code="MEMORY_STATE_CONFLICT",
                message="Memory is not pending confirmation",
                status_code=status.HTTP_409_CONFLICT,
                details={"state": memory.state},
            )
        memory.state = MemoryState.REJECTED.value
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def archive(db, memory: Memory) -> Memory:
        if memory.state != MemoryState.CONFIRMED.value:
            raise AppError(
                code="MEMORY_STATE_CONFLICT",
                message="Only confirmed memory can be archived",
                status_code=status.HTTP_409_CONFLICT,
                details={"state": memory.state},
            )
        memory.state = MemoryState.ARCHIVED.value
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory
