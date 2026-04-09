"""E2E smoke test — validates the full user journey via HTTP against a running stack."""

import time

import httpx
import pytest

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"


def ensure_stack_ready() -> None:
    try:
        response = httpx.get(HEALTH_URL, timeout=2.0)
    except httpx.HTTPError:
        pytest.skip("running stack not available")
    if response.status_code != 200:
        pytest.skip("running stack not available")


def wait_for_task(task_id: str, headers: dict[str, str], attempts: int = 30, interval: float = 1.0) -> dict:
    for _ in range(attempts):
        response = httpx.get(f"{BASE_URL}/tasks/{task_id}", headers=headers, timeout=10.0)
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in ("succeeded", "failed", "blocked"):
            return payload
        time.sleep(interval)
    raise AssertionError(f"Task {task_id} did not reach terminal state")


class TestE2ESmoke:
    def test_health_check(self) -> None:
        ensure_stack_ready()
        response = httpx.get(HEALTH_URL, timeout=5.0)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_provider_health(self) -> None:
        ensure_stack_ready()
        response = httpx.get(f"{BASE_URL}/provider/health", timeout=10.0)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded", "mock")
        assert data["mode"] in ("live", "mock")

    def test_full_user_journey(self) -> None:
        ensure_stack_ready()
        email = f"e2e-{int(time.time())}@test.com"
        register = httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": "test123456"}, timeout=10.0)
        assert register.status_code == 201
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        avatar = httpx.post(
            f"{BASE_URL}/avatars",
            headers=headers,
            json={"name": "E2E Avatar", "goal": "Test the full stack", "visibility": "private"},
            timeout=10.0,
        )
        assert avatar.status_code == 201
        avatar_id = avatar.json()["id"]

        persona = httpx.post(
            f"{BASE_URL}/avatars/{avatar_id}/persona/generate",
            headers=headers,
            json={"samples": ["I like tests."]},
            timeout=60.0,
        )
        assert persona.status_code == 201

        agent = httpx.post(
            f"{BASE_URL}/avatars/{avatar_id}/agents",
            headers=headers,
            json={"name": "E2E Agent", "role_prompt": "Test agent", "permissions": ["task:run"]},
            timeout=10.0,
        )
        assert agent.status_code == 201
        agent_id = agent.json()["id"]

        task = httpx.post(
            f"{BASE_URL}/tasks",
            headers=headers,
            json={"avatar_id": avatar_id, "agent_id": agent_id, "input": "Hello e2e"},
            timeout=10.0,
        )
        assert task.status_code == 201
        assert task.json()["status"] == "pending"

        completed_task = wait_for_task(task.json()["task_id"], headers)
        assert completed_task["status"] in ("succeeded", "blocked", "failed")

        audit = httpx.get(f"{BASE_URL}/audit", headers=headers, timeout=10.0)
        assert audit.status_code == 200
