"""Provider unit tests — covers retry logic, health check caching, and explicit live/mock handling."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.provider import OllamaProvider, ProviderUnavailableError


class TestOllamaProviderHealthCheck:
    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_health_check_caches_result(self) -> None:
        provider = OllamaProvider()
        with patch("app.services.provider.httpx.Client") as mock_client:
            version_response = MagicMock()
            version_response.json.return_value = {"version": "0.9.0"}
            version_response.raise_for_status = MagicMock()

            tags_response = MagicMock()
            tags_response.json.return_value = {"models": [{"name": "test-model"}]}
            tags_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.side_effect = [version_response, tags_response]
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = provider.health_check()
            assert result["status"] == "ok"
            assert result["model"] == "test-model"
            assert result["mode"] == "live"
            assert result["version"] == "0.9.0"
            assert result["chat_model_available"] is True
            assert provider._available is True

    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_health_check_returns_degraded_on_failure(self) -> None:
        provider = OllamaProvider()
        with patch("app.services.provider.httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = MagicMock(return_value=MagicMock(get=MagicMock(side_effect=Exception("connection refused"))))
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = provider.health_check(force=True)
            assert result["status"] == "degraded"
            assert result["mode"] == "live"
            assert result["version"] == "unknown"
            assert result["chat_model_available"] is False
            assert provider._available is False

    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_health_check_returns_degraded_when_only_embedding_models_exist(self) -> None:
        provider = OllamaProvider()
        with patch("app.services.provider.httpx.Client") as mock_client:
            version_response = MagicMock()
            version_response.json.return_value = {"version": "0.1.28"}
            version_response.raise_for_status = MagicMock()

            tags_response = MagicMock()
            tags_response.json.return_value = {
                "models": [
                    {
                        "name": "bge-m3:latest",
                        "details": {"family": "bert", "families": ["bert"]},
                    }
                ]
            }
            tags_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.side_effect = [version_response, tags_response]
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = provider.health_check(force=True)
            assert result["status"] == "degraded"
            assert result["model"] == provider.settings.ollama_model
            assert result["version"] == "0.1.28"
            assert result["chat_model_available"] is False
            assert "No chat-capable Ollama model available" in result["message"]
            assert provider._available is False

    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_health_check_prefers_configured_chat_model(self) -> None:
        provider = OllamaProvider()
        provider.settings.ollama_model = "qwen3.5:7b-instruct-q4_0"
        with patch("app.services.provider.httpx.Client") as mock_client:
            version_response = MagicMock()
            version_response.json.return_value = {"version": "0.9.0"}
            version_response.raise_for_status = MagicMock()

            tags_response = MagicMock()
            tags_response.json.return_value = {
                "models": [
                    {"name": "bge-m3:latest", "details": {"family": "bert", "families": ["bert"]}},
                    {"name": "qwen3.5:7b-instruct-q4_0", "details": {"family": "qwen3", "families": ["qwen3"]}},
                    {"name": "llama3.2:latest", "details": {"family": "llama", "families": ["llama"]}},
                ]
            }
            tags_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.side_effect = [version_response, tags_response]
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = provider.health_check(force=True)
            assert result["status"] == "ok"
            assert result["model"] == "qwen3.5:7b-instruct-q4_0"
            assert result["version"] == "0.9.0"
            assert result["chat_model_available"] is True
            assert provider._available is True

    @patch.dict("os.environ", {"PROVIDER_MODE": "mock"}, clear=False)
    def test_chat_returns_mock_in_mock_mode(self) -> None:
        provider = OllamaProvider()
        result = provider.chat("test prompt")
        assert "[Mock Mode]" in result
        assert provider.health_check()["message"] == "Provider running in mock mode."

    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_chat_retries_on_connection_error(self) -> None:
        provider = OllamaProvider()

        version_response = MagicMock()
        version_response.json.return_value = {"version": "0.9.0"}
        version_response.raise_for_status = MagicMock()

        health_response = MagicMock()
        health_response.json.return_value = {"models": [{"name": "test-model"}]}
        health_response.raise_for_status = MagicMock()

        success_response = MagicMock()
        success_response.json.return_value = {"message": {"content": "retry success"}}
        success_response.raise_for_status = MagicMock()

        with patch("app.services.provider.httpx.Client") as mock_client, patch("app.services.provider.time.sleep"):
            health_instance = MagicMock()
            health_instance.get.side_effect = [version_response, health_response]

            first_chat_instance = MagicMock()
            first_chat_instance.post.side_effect = Exception("connection reset")

            second_chat_instance = MagicMock()
            second_chat_instance.post.side_effect = Exception("connection reset")

            third_chat_instance = MagicMock()
            third_chat_instance.post.return_value = success_response

            mock_client.return_value.__enter__ = MagicMock(
                side_effect=[health_instance, first_chat_instance, second_chat_instance, third_chat_instance]
            )
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = provider.chat("test prompt", max_retries=2)
            assert result == "retry success"

    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_chat_raises_when_unavailable_in_live_mode(self) -> None:
        provider = OllamaProvider()

        with patch("app.services.provider.httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = MagicMock(return_value=MagicMock(get=MagicMock(side_effect=Exception("down"))))
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(ProviderUnavailableError) as exc_info:
                provider.chat("test prompt", max_retries=1)
            assert "Version: unknown" in str(exc_info.value)
            assert provider._available is False


class TestOllamaProviderEmbed:
    @patch.dict("os.environ", {"PROVIDER_MODE": "live"}, clear=False)
    def test_embed_returns_hash_on_failure(self) -> None:
        provider = OllamaProvider()
        provider._available = False
        result = provider.embed("test text")
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)
