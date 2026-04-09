from collections.abc import Iterator

from app.db.base import Base
from app.models import Agent, AuditLog, Avatar, Memory, Persona, Task, User

__all__ = ["Base", "User", "Avatar", "Persona", "Agent", "Task", "Memory", "AuditLog"]


def iter_models() -> Iterator[type[Base]]:
    yield User
    yield Avatar
    yield Persona
    yield Agent
    yield Task
    yield Memory
    yield AuditLog
