import os

from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///./data/test_smoke.db'
os.environ['JWT_SECRET'] = 'test-secret'
os.environ['PROVIDER_MODE'] = 'mock'

from app.main import app  # noqa: E402

client = TestClient(app)


def test_smoke_health_and_metrics() -> None:
    health = client.get('/health')
    metrics = client.get('/metrics')

    assert health.status_code == 200
    assert health.json()['status'] == 'ok'
    assert health.json()['checks']['db'] == 'ok'
    assert health.json()['checks']['provider'] == 'mock'
    assert health.json()['provider']['mode'] == 'mock'
    assert health.json()['provider']['status'] == 'mock'
    assert health.json()['provider']['version'] == 'mock'
    assert health.json()['provider']['chat_model_available'] is True
    assert health.json()['provider']['base_url'] == 'http://localhost:11434'
    assert health.json()['provider']['message'] == 'Provider running in mock mode.'
    assert metrics.status_code == 200
    assert metrics.json()['metrics']['version'] == '0.1.0'
    assert metrics.json()['metrics']['provider_mode'] == 'mock'
    assert metrics.json()['metrics']['provider_status'] == 'mock'
    assert metrics.json()['metrics']['provider_version'] == 'mock'
    assert metrics.json()['metrics']['provider_chat_model_available'] is True
    assert metrics.json()['metrics']['provider_base_url'] == 'http://localhost:11434'
    assert metrics.json()['metrics']['provider_message'] == 'Provider running in mock mode.'
