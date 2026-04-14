import logging
import os
import time
from uuid import uuid4

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Default model if auto-detection finds nothing
DEFAULT_MODEL = "qwen3.5:latest"
EMBEDDING_FAMILIES = {"bert"}
EMBEDDING_MODEL_KEYWORDS = ("embedding", "reranker", "bge")
UNKNOWN_VERSION = "unknown"


class ProviderUnavailableError(RuntimeError):
    pass


class OllamaProvider:
    """Ollama LLM Provider with retry, timeout, and explicit mode handling."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = self.settings.ollama_model or DEFAULT_MODEL
        self.mode = os.getenv("PROVIDER_MODE", "live").strip().lower() or "live"
        self._available: bool | None = None
        self._last_health_check: float = 0.0
        self._health_cache_ttl: float = 30.0  # cache health for 30s
        self._version: str = UNKNOWN_VERSION
        self._chat_model_available: bool = False

    # ------------------------------------------------------------------
    # Health check (cached)
    # ------------------------------------------------------------------

    def health_check(self, *, force: bool = False) -> dict:
        """Check Ollama availability. Result is cached for ``_health_cache_ttl`` seconds."""
        if self.mode == "mock":
            self._available = False
            self._version = "mock"
            self._chat_model_available = True
            return self._health_payload(status="mock")

        now = time.monotonic()
        if not force and self._available is not None and (now - self._last_health_check) < self._health_cache_ttl:
            return self._health_payload(status="ok" if self._available else "degraded")

        try:
            with httpx.Client(base_url=self.settings.ollama_base_url, timeout=5.0) as client:
                self._version = self._fetch_version(client)
                response = client.get("/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                selected_model = self._select_chat_model(models)
                self._chat_model_available = selected_model is not None
                if selected_model:
                    self.model = selected_model
                    self._available = True
                    self._last_health_check = now
                    return self._health_payload(status="ok")

                logger.warning("No chat-capable Ollama model found in tags; keeping configured model %s", self.model)
                self._available = False
                self._last_health_check = now
                return self._health_payload(status="degraded")
        except Exception as exc:
            logger.warning("Ollama health check failed: %s", exc)
            self._available = False
            self._chat_model_available = False
            self._last_health_check = now
            return self._health_payload(status="degraded")

    # ------------------------------------------------------------------
    # Chat with retry
    # ------------------------------------------------------------------

    def chat(self, prompt: str, *, max_retries: int | None = None) -> str:
        """Send a chat completion request with automatic retries."""
        if self.mode == "mock":
            return self._mock_response(prompt)

        retries = self.settings.ollama_max_retries if max_retries is None else max_retries
        health = self.health_check()
        if self._available is False:
            raise ProviderUnavailableError(
                f"Ollama unavailable at {self.settings.ollama_base_url}. "
                f"Version: {health.get('version', UNKNOWN_VERSION)}. "
                f"Switch PROVIDER_MODE=mock for demo mode or start Ollama with model {self.model}."
            )

        last_exc: Exception | None = None
        for attempt in range(1 + retries):
            try:
                with httpx.Client(
                    base_url=self.settings.ollama_base_url,
                    timeout=httpx.Timeout(connect=10.0, read=float(self.settings.ollama_chat_timeout), write=10.0, pool=10.0),
                    transport=httpx.HTTPTransport(retries=1),
                ) as client:
                    response = client.post(
                        "/api/chat",
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "stream": False,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                    if not content:
                        logger.warning("Ollama returned empty content on attempt %d", attempt + 1)
                        last_exc = ValueError("Empty response from Ollama")
                        continue
                    return content
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                status_code = exc.response.status_code
                if 400 <= status_code < 500 and status_code != 429:
                    logger.error("Ollama client error %s (non-retryable): %s", status_code, exc)
                    break
                logger.warning("Ollama HTTP %s on attempt %d/%d: %s", status_code, attempt + 1, 1 + retries, exc)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
                last_exc = exc
                logger.warning("Ollama connection error on attempt %d/%d: %s", attempt + 1, 1 + retries, exc)
            except Exception as exc:
                last_exc = exc
                logger.warning("Ollama unexpected error on attempt %d/%d: %s", attempt + 1, 1 + retries, exc)

            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))

        self._available = False
        self._chat_model_available = False
        self._last_health_check = time.monotonic()
        logger.error("Ollama unavailable after %d retries: %s", retries, last_exc)
        raise ProviderUnavailableError(
            f"Ollama unavailable after retries at {self.settings.ollama_base_url}. "
            f"Version: {self._version}. Last error: {last_exc}"
        )

    # ------------------------------------------------------------------
    # Embeddings with retry
    # ------------------------------------------------------------------

    def embed(self, text: str, *, max_retries: int = 1) -> list[float]:
        """Get text embeddings with retry. Returns a deterministic hash on failure."""
        self.health_check()
        if self._available is False:
            return self._hash_embedding(text)

        for attempt in range(1 + max_retries):
            try:
                with httpx.Client(
                    base_url=self.settings.ollama_base_url,
                    timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0),
                ) as client:
                    response = client.post("/api/embeddings", json={"model": self.model, "prompt": text})
                    response.raise_for_status()
                    data = response.json()
                    embedding = data.get("embedding")
                    if embedding and isinstance(embedding, list):
                        return embedding
                    logger.warning("Ollama returned empty embedding on attempt %d", attempt + 1)
            except Exception as exc:
                logger.warning("Ollama embed error on attempt %d/%d: %s", attempt + 1, 1 + max_retries, exc)

            if attempt < max_retries:
                time.sleep(1)

        return self._hash_embedding(text)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_chat_capable_model(model: dict) -> bool:
        name = str(model.get("name", "")).lower()
        details = model.get("details", {}) or {}
        families = [str(family).lower() for family in details.get("families", [])]
        family = str(details.get("family", "")).lower()

        if any(keyword in name for keyword in EMBEDDING_MODEL_KEYWORDS):
            return False
        if family in EMBEDDING_FAMILIES:
            return False
        if any(family_name in EMBEDDING_FAMILIES for family_name in families):
            return False
        return bool(name)

    def _select_chat_model(self, models: list[dict]) -> str | None:
        preferred = (self.settings.ollama_model or DEFAULT_MODEL).strip().lower()
        chat_models = [model for model in models if self._is_chat_capable_model(model)]
        if not chat_models:
            return None

        for model in chat_models:
            model_name = str(model.get("name", ""))
            if model_name.lower() == preferred:
                return model_name

        return str(chat_models[0].get("name", self.model))

    @staticmethod
    def _fetch_version(client: httpx.Client) -> str:
        try:
            response = client.get("/api/version")
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                version = payload.get("version")
                if version:
                    return str(version)
            if isinstance(payload, str) and payload.strip():
                return payload.strip()
        except Exception:
            pass
        return UNKNOWN_VERSION

    def _health_payload(self, *, status: str) -> dict:
        message = None
        if self.mode == "mock":
            message = "Provider running in mock mode."
        elif status == "degraded" and not self._chat_model_available:
            message = (
                f"No chat-capable Ollama model available at {self.settings.ollama_base_url}. "
                f"Current version: {self._version}. Configured model: {self.model}."
            )

        return {
            "status": status,
            "model": self.model,
            "mode": self.mode,
            "version": self._version,
            "chat_model_available": self._chat_model_available,
            "base_url": self.settings.ollama_base_url,
            "message": message,
        }

    def _mock_response(self, prompt: str) -> str:
        return (
            f"[Mock Mode] Digital Avatar simulated response.\n\n"
            f"Input received: {prompt[:300]}{'...' if len(prompt) > 300 else ''}\n\n"
            f"To enable live mode, ensure Ollama is running at {self.settings.ollama_base_url} "
            f"and run: ollama pull {self.model}"
        )

    @staticmethod
    def _hash_embedding(text: str) -> list[float]:
        """Deterministic pseudo-embedding from hash, same dimensionality as typical models."""
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [int(h[i:i+2], 16) / 255.0 for i in range(0, min(len(h), 64), 2)]

    def model_info(self) -> dict:
        return {
            "provider": "ollama",
            "mode": self.mode,
            "status": "ok" if self._available else ("mock" if self.mode == "mock" else "degraded"),
            "model": self.model,
            "version": self._version,
            "chat_model_available": self._chat_model_available,
            "base_url": self.settings.ollama_base_url,
        }
