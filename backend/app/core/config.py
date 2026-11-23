from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "SemiTest AI"
    app_env: str = "development"
    simulation_mode: str = "SIMULATION_ONLY"
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'backend' / 'data' / 'semitest.db'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_bytes: int = 5 * 1024 * 1024
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("simulation_mode")
    @classmethod
    def enforce_simulation_only(cls, value: str) -> str:
        if value != "SIMULATION_ONLY":
            raise ValueError("SemiTest AI must run in SIMULATION_ONLY mode")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
