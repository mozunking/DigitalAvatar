import httpx
import pytest

BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"
WEB_BASE_URL = "http://localhost:4173"


def ensure_stack_ready() -> None:
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
    except httpx.HTTPError:
        pytest.skip("compose stack not available")
    if response.status_code != 200:
        pytest.skip("compose stack not available")


def test_compose_stack_health_endpoints() -> None:
    ensure_stack_ready()
    health = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    provider = httpx.get(f"{API_BASE_URL}/provider/health", timeout=10.0)
    assert provider.status_code == 200
    assert provider.json()["mode"] in {"mock", "live"}
    assert provider.json()["status"] in {"mock", "ok", "degraded"}


def test_compose_stack_web_entrypoint() -> None:
    ensure_stack_ready()
    response = httpx.get(WEB_BASE_URL, timeout=10.0)
    assert response.status_code == 200
    assert "<div id=\"app\"></div>" in response.text
