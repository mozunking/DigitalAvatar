from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    trace_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    trace_id: str


class CreateAvatarRequest(BaseModel):
    name: str
    goal: str
    visibility: str = "private"


class UpdateAvatarRequest(BaseModel):
    name: str
    goal: str
    visibility: str = "private"


class AvatarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    goal: str
    visibility: str
    status: str
    created_at: datetime


class PersonaGenerateRequest(BaseModel):
    samples: list[str]
    template_id: str | None = None


class PersonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    avatar_id: str
    summary: str
    source_count: int
    version: int
    is_current: bool
    created_at: datetime


class CreateAgentRequest(BaseModel):
    name: str
    role_prompt: str
    permissions: list[str] = Field(default_factory=list)


class UpdateAgentStatusRequest(BaseModel):
    status: str


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    avatar_id: str
    name: str
    role_prompt: str
    permissions: list[str] = Field(default_factory=list)
    status: str
    created_at: datetime

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "AgentResponse":
        """Override to deserialize JSON permissions string from DB."""
        if hasattr(obj, "permissions") and isinstance(obj.permissions, str):
            try:
                obj.permissions = json.loads(obj.permissions)
            except (json.JSONDecodeError, TypeError):
                obj.permissions = []
        return super().model_validate(obj, **kwargs)


class CreateTaskRequest(BaseModel):
    avatar_id: str
    agent_id: str
    input: str
    trace_id: str | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    status: str
    trace_id: str
    result: str | None = None
    error: str | None = None
    worker_id: str | None = None
    claimed_at: datetime | None = None
    started_at: datetime | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "TaskResponse":
        """Map DB fields to API fields: id->task_id, result_text->result, error_text->error."""
        if hasattr(obj, "id"):
            data = {
                "task_id": getattr(obj, "id", ""),
                "status": getattr(obj, "status", ""),
                "trace_id": getattr(obj, "trace_id", ""),
                "result": getattr(obj, "result_text", None),
                "error": getattr(obj, "error_text", None),
                "worker_id": getattr(obj, "worker_id", None),
                "claimed_at": getattr(obj, "claimed_at", None),
                "started_at": getattr(obj, "started_at", None),
                "created_at": getattr(obj, "created_at", None),
                "completed_at": getattr(obj, "completed_at", None),
            }
            return cls(**data)
        return super().model_validate(obj, **kwargs)


class MemoryDecisionRequest(BaseModel):
    reason: str | None = None


class MemorySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    avatar_id: str
    task_id: str | None
    type: str
    sensitivity: str
    state: str
    excerpt: str
    source_type: str | None = None
    created_at: datetime

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "MemorySummaryResponse":
        if hasattr(obj, "content"):
            data = {
                "id": getattr(obj, "id", ""),
                "avatar_id": getattr(obj, "avatar_id", ""),
                "task_id": getattr(obj, "task_id", None),
                "type": getattr(obj, "type", ""),
                "sensitivity": getattr(obj, "sensitivity", ""),
                "state": getattr(obj, "state", ""),
                "excerpt": getattr(obj, "content", "")[:120],
                "source_type": getattr(obj, "source_type", None),
                "created_at": getattr(obj, "created_at", None),
            }
            return cls(**data)
        return super().model_validate(obj, **kwargs)


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    avatar_id: str
    task_id: str | None
    type: str
    sensitivity: str
    state: str
    content: str
    source_type: str | None = None
    created_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trace_id: str
    actor: str
    action: str
    resource_type: str
    resource_id: str
    result: str
    request_summary: str
    policy_hits: str
    hash_prev: str | None
    hash_self: str
    created_at: datetime


class PaginatedResponse(BaseModel):
    items: list[Any]
    page: int = 1
    page_size: int = 20
    total: int = 0


class MemorySummaryPageResponse(BaseModel):
    items: list[MemorySummaryResponse]
    page: int = 1
    page_size: int = 20
    total: int = 0


class MemoryPageResponse(BaseModel):
    items: list[MemoryResponse]
    page: int = 1
    page_size: int = 20
    total: int = 0
