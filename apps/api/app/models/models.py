from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import hash_password
from app.db.base import Base


class AvatarStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AgentStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    DISABLED = "disabled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class MemoryState(str, Enum):
    CAPTURED = "captured"
    PENDING_CONFIRM = "pending_confirm"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class MemoryType(str, Enum):
    PROFILE = "profile"
    EPISODIC = "episodic"
    KNOWLEDGE = "knowledge"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255), default="Demo User")
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    avatars: Mapped[list[Avatar]] = relationship(back_populates="user")

    @classmethod
    def demo(cls) -> "User":
        return cls(email="demo@example.com", hashed_password=hash_password("demo123456"), display_name="Demo User")


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    status: Mapped[str] = mapped_column(String(20), default=AvatarStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="avatars")
    personas: Mapped[list[Persona]] = relationship(back_populates="avatar")
    agents: Mapped[list[Agent]] = relationship(back_populates="avatar")
    tasks: Mapped[list[Task]] = relationship(back_populates="avatar")
    memories: Mapped[list[Memory]] = relationship(back_populates="avatar")


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    avatar_id: Mapped[str] = mapped_column(ForeignKey("avatars.id"), index=True)
    summary: Mapped[str] = mapped_column(Text)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    avatar: Mapped[Avatar] = relationship(back_populates="personas")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    avatar_id: Mapped[str] = mapped_column(ForeignKey("avatars.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    role_prompt: Mapped[str] = mapped_column(Text)
    permissions: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default=AgentStatus.READY.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    avatar: Mapped[Avatar] = relationship(back_populates="agents")
    tasks: Mapped[list[Task]] = relationship(back_populates="agent")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    avatar_id: Mapped[str] = mapped_column(ForeignKey("avatars.id"), index=True)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True, default=lambda: uuid4().hex)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.PENDING.value, index=True)
    worker_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    avatar: Mapped[Avatar] = relationship(back_populates="tasks")
    agent: Mapped[Agent] = relationship(back_populates="tasks")
    memories: Mapped[list[Memory]] = relationship(back_populates="task")


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    avatar_id: Mapped[str] = mapped_column(ForeignKey("avatars.id"), index=True)
    task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(20), default=MemoryType.EPISODIC.value, index=True)
    sensitivity: Mapped[str] = mapped_column(String(20), default="normal")
    state: Mapped[str] = mapped_column(String(20), default=MemoryState.PENDING_CONFIRM.value, index=True)
    content: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(50), default="task")
    source_ref_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    avatar: Mapped[Avatar] = relationship(back_populates="memories")
    task: Mapped[Task | None] = relationship(back_populates="memories")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token_type: Mapped[str] = mapped_column(String(20), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    actor: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(50), index=True)
    resource_id: Mapped[str] = mapped_column(String(36), index=True)
    result: Mapped[str] = mapped_column(String(20))
    request_summary: Mapped[str] = mapped_column(Text, default="")
    policy_hits: Mapped[str] = mapped_column(Text, default="[]")
    hash_prev: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hash_self: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
