from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Digital Avatar API"
    app_env: str = Field(default="local", alias="APP_ENV")
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me", alias="JWT_SECRET")
    access_token_expire_minutes: int = Field(default=15, alias="JWT_ACCESS_TTL_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="JWT_REFRESH_TTL_DAYS")
    algorithm: str = "HS256"
    database_url: str = Field(default="sqlite:///./data/app.db", alias="DATABASE_URL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3.5:7b-instruct-q4_0", alias="OLLAMA_MODEL")
    ollama_chat_timeout: int = Field(default=120, alias="OLLAMA_CHAT_TIMEOUT")
    ollama_max_retries: int = Field(default=2, alias="OLLAMA_MAX_RETRIES")
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    log_dir: Path = Field(default=Path("./logs"), alias="LOG_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    return settings
