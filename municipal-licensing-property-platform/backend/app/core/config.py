from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_secret(name: str, default: str | None = None) -> str | None:
    direct = os.getenv(name)
    if direct:
        return direct
    file_name = os.getenv(f"{name}_FILE")
    if file_name:
        path = Path(file_name)
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    return default


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Municipal Licensing & Property Platform"
    app_slug: str = "municipal-platform"
    environment: Literal["development", "staging", "production"] = "production"
    api_v1_prefix: str = "/api/v1"
    timezone: str = "Asia/Kolkata"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(default="postgresql+psycopg://app:app@db:5432/appdb")
    redis_url: str = Field(default="redis://redis:6379/0")

    keycloak_issuer_url: AnyHttpUrl = Field(default="http://keycloak:8080/realms/municipal")
    keycloak_jwks_url_override: AnyHttpUrl | None = Field(default=None, alias="keycloak_jwks_url")
    keycloak_client_id: str = "municipal-frontend"
    keycloak_audience: str = "account"
    keycloak_verify_tls: bool = False
    keycloak_jwks_cache_ttl_seconds: int = 900

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ]
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    logs_root: Path = Path("/srv/logs")
    app_log_name: str = "application.jsonl"
    audit_log_name: str = "audit.jsonl"
    log_max_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 10

    docs_root: Path = Path("/srv/documents")
    backups_root: Path = Path("/srv/backups")
    runtime_root: Path = Path("/srv/runtime")

    max_upload_bytes: int = 10 * 1024 * 1024
    allowed_file_types: list[str] = Field(
        default_factory=lambda: [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "text/plain",
        ]
    )

    request_timeout_seconds: float = 5.0
    outbound_connect_timeout_seconds: float = 2.0
    outbound_read_timeout_seconds: float = 5.0
    retry_max_attempts: int = 3
    retry_backoff_base_seconds: float = 0.5
    retry_budget_per_minute: int = 20
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_reset_seconds: int = 60
    auth_bulkhead_limit: int = 20
    storage_bulkhead_limit: int = 10

    rate_limit_per_minute: int = 120
    rate_limit_burst: int = 30
    failed_request_penalty_seconds: int = 60

    idempotency_ttl_hours: int = 24
    audit_retention_days: int = 365
    idempotency_retention_days: int = 7
    backup_retention_days: int = 30
    backup_validation_retention_days: int = 30

    metrics_enabled: bool = True
    enable_openapi: bool = True

    app_encryption_key: str = Field(default="")
    disk_pressure_threshold_percent: int = 85
    minimum_free_disk_mb: int = 1024

    celery_task_soft_time_limit_seconds: int = 300
    celery_task_hard_time_limit_seconds: int = 360

    @field_validator("allowed_origins", "allowed_file_types", mode="before")
    @classmethod
    def _split_csv(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def keycloak_jwks_url(self) -> str:
        if self.keycloak_jwks_url_override is not None:
            return str(self.keycloak_jwks_url_override).rstrip("/")
        return f"{str(self.keycloak_issuer_url).rstrip('/')}/protocol/openid-connect/certs"

    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.enable_openapi else None

    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.enable_openapi else None

    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.enable_openapi else None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()

    database_url = _read_secret("DATABASE_URL")
    if database_url:
        settings.database_url = database_url

    redis_url = _read_secret("REDIS_URL")
    if redis_url:
        settings.redis_url = redis_url

    encryption_key = _read_secret("APP_ENCRYPTION_KEY")
    if encryption_key:
        settings.app_encryption_key = encryption_key

    settings.logs_root.mkdir(parents=True, exist_ok=True)
    settings.docs_root.mkdir(parents=True, exist_ok=True)
    settings.backups_root.mkdir(parents=True, exist_ok=True)
    settings.runtime_root.mkdir(parents=True, exist_ok=True)

    if not settings.app_encryption_key:
        raise RuntimeError(
            "APP_ENCRYPTION_KEY or APP_ENCRYPTION_KEY_FILE must be supplied. "
            "Generate a Fernet-compatible key with scripts/generate_secrets.ps1."
        )
    return settings
