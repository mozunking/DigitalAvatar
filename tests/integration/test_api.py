"""Integration tests for the Digital Avatar API — updated for nested route structure."""

import os
import time
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./data/test_app.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["PROVIDER_MODE"] = "mock"

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.bootstrap import ensure_seed_data  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_seed_data(db)


def auth_headers() -> dict[str, str]:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}


def wait_for_task_terminal(task_id: str, headers: dict[str, str], attempts: int = 30, interval: float = 0.1) -> dict:
    for _ in range(attempts):
        response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in {"succeeded", "failed", "blocked"}:
            return payload
        time.sleep(interval)
    pytest.fail(f"Task {task_id} did not reach terminal state")


# ------------------------------------------------------------------ #
# Health & Auth
# ------------------------------------------------------------------ #


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Digital Avatar API"
    assert payload["checks"]["db"] == "ok"
    assert payload["checks"]["provider"] == "mock"
    assert payload["provider"]["mode"] == "mock"
    assert payload["provider"]["status"] == "mock"
    assert payload["provider"]["version"] == "mock"
    assert payload["provider"]["chat_model_available"] is True
    assert payload["provider"]["message"] == "Provider running in mock mode."


def test_login_and_me_flow() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "demo@example.com"


def test_unauthorized_access_uses_frozen_error_code() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


# ------------------------------------------------------------------ #
# MVP mainline flow with nested routes
# ------------------------------------------------------------------ #


def test_mvp_mainline_flow() -> None:
    headers = auth_headers()

    avatar = client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Demo Avatar", "goal": "Operate safely", "visibility": "private"},
    )
    assert avatar.status_code == 201
    avatar_id = avatar.json()["id"]

    persona = client.post(
        f"/api/v1/avatars/{avatar_id}/persona/generate",
        headers=headers,
        json={"samples": ["I prefer concise updates.", "Keep decisions traceable."]},
    )
    assert persona.status_code == 201
    assert persona.json()["avatar_id"] == avatar_id
    persona_id = persona.json()["id"]

    activate = client.post(
        f"/api/v1/personas/{persona_id}/activate",
        headers=headers,
    )
    assert activate.status_code == 200

    agent = client.post(
        f"/api/v1/avatars/{avatar_id}/agents",
        headers=headers,
        json={"name": "General Task Agent", "role_prompt": "Be safe and concise.", "permissions": ["task:run"]},
    )
    assert agent.status_code == 201
    agent_id = agent.json()["id"]
    assert isinstance(agent.json()["permissions"], list)

    trace_id = f"trace-{uuid.uuid4().hex}"
    task = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"avatar_id": avatar_id, "agent_id": agent_id, "input": "Summarize my priorities.", "trace_id": trace_id},
    )
    assert task.status_code == 201
    task_payload = task.json()
    assert task_payload["status"] == "pending"
    assert task_payload["trace_id"] == trace_id

    completed_task = wait_for_task_terminal(task_payload["task_id"], headers)
    assert completed_task["status"] == "succeeded"
    assert completed_task["result"]

    memories = client.get(f"/api/v1/avatars/{avatar_id}/memories/pending", headers=headers)
    assert memories.status_code == 200
    assert memories.json()["total"] >= 1
    memory_id = memories.json()["items"][0]["id"]

    confirm = client.post(f"/api/v1/memories/{memory_id}/confirm", headers=headers, json={"reason": "looks good"})
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmed"

    conflict = client.post(f"/api/v1/memories/{memory_id}/reject", headers=headers, json={})
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "MEMORY_STATE_CONFLICT"

    audit = client.get("/api/v1/audit", params={"trace_id": trace_id}, headers=headers)
    assert audit.status_code == 200
    assert audit.json()["total"] >= 1
    items = audit.json()["items"]
    assert any(item["trace_id"] == trace_id for item in items)
    assert any(item["action"] == "task_created" for item in items)
    assert any(item["action"] == "task_started" for item in items)
    assert any(item["action"] == "task_completed" for item in items)


# ------------------------------------------------------------------ #
# Policy blocking
# ------------------------------------------------------------------ #


def test_policy_block_writes_audit_record() -> None:
    headers = auth_headers()

    avatar = client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Risk Avatar", "goal": "Test policy", "visibility": "private"},
    )
    avatar_id = avatar.json()["id"]

    agent = client.post(
        f"/api/v1/avatars/{avatar_id}/agents",
        headers=headers,
        json={"name": "Risk Agent", "role_prompt": "Be safe.", "permissions": ["task:run"]},
    )
    agent_id = agent.json()["id"]

    trace_id = f"blocked-{uuid.uuid4().hex}"
    task = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"avatar_id": avatar_id, "agent_id": agent_id, "input": "please drop database now", "trace_id": trace_id},
    )
    assert task.status_code == 201
    assert task.json()["status"] == "pending"

    blocked_task = wait_for_task_terminal(task.json()["task_id"], headers)
    assert blocked_task["status"] == "blocked"

    audit = client.get("/api/v1/audit", params={"trace_id": trace_id}, headers=headers)
    assert audit.status_code == 200
    items = audit.json()["items"]
    assert any(item["result"] == "blocked" for item in items)
    assert any(item["action"] == "task_blocked" for item in items)


# ------------------------------------------------------------------ #
# Audit completeness — verify all write operations produce audit logs
# ------------------------------------------------------------------ #


def test_audit_logs_for_agent_crud() -> None:
    headers = auth_headers()

    avatar = client.post("/api/v1/avatars", headers=headers, json={"name": "Audit Avatar", "goal": "test", "visibility": "private"})
    avatar_id = avatar.json()["id"]

    agent = client.post(
        f"/api/v1/avatars/{avatar_id}/agents",
        headers=headers,
        json={"name": "Audit Agent", "role_prompt": "test", "permissions": []},
    )
    agent_id = agent.json()["id"]

    audit = client.get("/api/v1/audit", params={"resource_type": "agent"}, headers=headers)
    assert audit.json()["total"] >= 1
    assert any(item["action"] == "agent_created" for item in audit.json()["items"])

    client.patch(f"/api/v1/avatars/{avatar_id}/agents/{agent_id}", headers=headers, json={"status": "disabled"})
    audit = client.get("/api/v1/audit", params={"resource_type": "agent"}, headers=headers)
    assert any(item["action"] == "agent_disabled" for item in audit.json()["items"])


def test_audit_logs_for_memory_operations() -> None:
    headers = auth_headers()

    avatar = client.post("/api/v1/avatars", headers=headers, json={"name": "Mem Audit", "goal": "test", "visibility": "private"})
    avatar_id = avatar.json()["id"]
    agent = client.post(
        f"/api/v1/avatars/{avatar_id}/agents",
        headers=headers,
        json={"name": "Mem Agent", "role_prompt": "test", "permissions": ["task:run"]},
    )
    agent_id = agent.json()["id"]

    task = client.post("/api/v1/tasks", headers=headers, json={"avatar_id": avatar_id, "agent_id": agent_id, "input": "hello"})
    task_payload = wait_for_task_terminal(task.json()["task_id"], headers)
    assert task_payload["status"] == "succeeded"
    trace_id = task_payload["trace_id"]

    memories = client.get(f"/api/v1/avatars/{avatar_id}/memories/pending", headers=headers)
    assert memories.json()["total"] >= 1
    memory_id = memories.json()["items"][0]["id"]

    client.post(f"/api/v1/memories/{memory_id}/confirm", headers=headers, json={"reason": "approved"})
    audit = client.get("/api/v1/audit", params={"resource_type": "memory", "trace_id": trace_id}, headers=headers)
    assert any(item["action"] == "memory_captured" for item in audit.json()["items"])


# ------------------------------------------------------------------ #
# Avatar detail endpoint
# ------------------------------------------------------------------ #


def test_avatar_detail_endpoint() -> None:
    headers = auth_headers()

    avatar = client.post("/api/v1/avatars", headers=headers, json={"name": "Detail Test", "goal": "test", "visibility": "private"})
    avatar_id = avatar.json()["id"]

    detail = client.get(f"/api/v1/avatars/{avatar_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["name"] == "Detail Test"

    updated = client.put(f"/api/v1/avatars/{avatar_id}", headers=headers, json={"name": "Updated", "goal": "new goal", "visibility": "team"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"
