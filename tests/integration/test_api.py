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
    assert payload["provider"]["base_url"] == "http://localhost:11434"
    assert payload["provider"]["message"] == "Provider running in mock mode."


def test_login_and_me_flow() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "demo@example.com"


def test_refresh_rotates_token_and_invalidates_previous_refresh_token() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": payload["refresh_token"]})
    assert refreshed.status_code == 200
    refreshed_payload = refreshed.json()
    assert refreshed_payload["refresh_token"] != payload["refresh_token"]
    assert refreshed_payload["access_token"] != payload["access_token"]

    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": payload["refresh_token"]})
    assert reused.status_code == 401
    assert reused.json()["error"]["code"] == "UNAUTHORIZED"


def test_logout_revokes_access_and_refresh_tokens() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()
    headers = {"Authorization": f"Bearer {payload['access_token']}"}

    logout = client.post("/api/v1/auth/logout", headers=headers, json={"refresh_token": payload["refresh_token"]})
    assert logout.status_code == 204

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 401
    assert me.json()["error"]["code"] == "UNAUTHORIZED"

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": payload["refresh_token"]})
    assert refreshed.status_code == 401
    assert refreshed.json()["error"]["code"] == "UNAUTHORIZED"

    audit = client.get("/api/v1/audit", params={"resource_type": "user"}, headers=auth_headers())
    assert audit.status_code == 200
    assert any(item["action"] == "auth_logout" for item in audit.json()["items"])


def test_auth_audit_logs_include_login_and_refresh() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login.status_code == 200
    payload = login.json()

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": payload["refresh_token"]})
    assert refresh.status_code == 200

    headers = {"Authorization": f"Bearer {refresh.json()['access_token']}"}
    audit = client.get("/api/v1/audit", params={"resource_type": "user"}, headers=headers)
    assert audit.status_code == 200
    assert any(item["action"] == "auth_login" and item["result"] == "success" for item in audit.json()["items"])
    assert any(item["action"] == "auth_refresh" and item["result"] == "success" for item in audit.json()["items"])


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
    assert "content" in memories.json()["items"][0]
    assert "excerpt" not in memories.json()["items"][0]
    memory_id = memories.json()["items"][0]["id"]

    confirm = client.post(f"/api/v1/memories/{memory_id}/confirm", headers=headers, json={"reason": "looks good"})
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmed"

    memory_search = client.get(
        f"/api/v1/avatars/{avatar_id}/memories/search",
        headers=headers,
    )
    assert memory_search.status_code == 200
    assert memory_search.json()["total"] >= 1
    assert "excerpt" in memory_search.json()["items"][0]
    assert "content" not in memory_search.json()["items"][0]
    assert memory_search.json()["items"][0]["id"] == memory_id

    memory_detail = client.get(f"/api/v1/avatars/{avatar_id}/memories/{memory_id}", headers=headers)
    assert memory_detail.status_code == 200
    assert memory_detail.json()["id"] == memory_id
    assert memory_detail.json()["content"]

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

    client.patch(f"/api/v1/avatars/agents/{agent_id}", headers=headers, json={"status": "disabled"})
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

    updated = client.patch(f"/api/v1/avatars/{avatar_id}", headers=headers, json={"name": "Updated", "goal": "new goal", "visibility": "team"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"


def test_audit_logs_are_scoped_to_current_user() -> None:
    first_headers = auth_headers()
    first_avatar = client.post(
        "/api/v1/avatars",
        headers=first_headers,
        json={"name": "User One Avatar", "goal": "private scope", "visibility": "private"},
    )
    assert first_avatar.status_code == 201
    first_avatar_id = first_avatar.json()["id"]

    first_agent = client.post(
        f"/api/v1/avatars/{first_avatar_id}/agents",
        headers=first_headers,
        json={"name": "Scoped Agent", "role_prompt": "test", "permissions": ["task:run"]},
    )
    assert first_agent.status_code == 201

    register = client.post(
        "/api/v1/auth/register",
        json={"email": "second@example.com", "password": "secret123", "display_name": "Second User"},
    )
    assert register.status_code == 201
    second_headers = {"Authorization": f"Bearer {register.json()['access_token']}"}

    list_response = client.get("/api/v1/audit", headers=second_headers)
    assert list_response.status_code == 200
    assert all(item["resource_id"] != first_avatar_id for item in list_response.json()["items"])

    resource_response = client.get("/api/v1/audit", params={"resource_type": "avatar"}, headers=second_headers)
    assert resource_response.status_code == 200
    assert resource_response.json()["total"] == 0


def test_privacy_export_and_delete_cover_related_entities_and_audit() -> None:
    headers = auth_headers()

    avatar = client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Privacy Avatar", "goal": "cleanup", "visibility": "private"},
    )
    assert avatar.status_code == 201
    avatar_id = avatar.json()["id"]

    persona = client.post(
        f"/api/v1/avatars/{avatar_id}/persona/generate",
        headers=headers,
        json={"samples": ["I prefer concise updates.", "Keep evidence attached."]},
    )
    assert persona.status_code == 201

    agent = client.post(
        f"/api/v1/avatars/{avatar_id}/agents",
        headers=headers,
        json={"name": "Privacy Agent", "role_prompt": "Be safe.", "permissions": ["task:run"]},
    )
    assert agent.status_code == 201
    agent_id = agent.json()["id"]

    task = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"avatar_id": avatar_id, "agent_id": agent_id, "input": "Summarize my style."},
    )
    assert task.status_code == 201
    task_payload = wait_for_task_terminal(task.json()["task_id"], headers)
    assert task_payload["status"] == "succeeded"

    pending = client.get(f"/api/v1/avatars/{avatar_id}/memories/pending", headers=headers)
    assert pending.status_code == 200
    memory_id = pending.json()["items"][0]["id"]

    export_before = client.get("/api/v1/privacy/export", headers=headers)
    assert export_before.status_code == 200
    export_payload = export_before.json()
    assert any(item["id"] == avatar_id for item in export_payload["avatars"])
    assert any(item["avatar_id"] == avatar_id for item in export_payload["personas"])
    assert any(item["avatar_id"] == avatar_id for item in export_payload["agents"])
    assert any(item["id"] == memory_id for item in export_payload["memories"])
    assert any(item["resource_id"] == memory_id for item in export_payload["audit_logs"])

    delete_response = client.delete("/api/v1/privacy/delete", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    login_again = client.post("/api/v1/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert login_again.status_code == 401
