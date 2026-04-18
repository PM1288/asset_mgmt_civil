from __future__ import annotations

from cryptography.fernet import Fernet

from app.core.config import get_settings


def get_fernet() -> Fernet:
    settings = get_settings()
    return Fernet(settings.app_encryption_key.encode("utf-8"))


def encrypt_value(value: str | None) -> str | None:
    if value in (None, ""):
        return value
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value: str | None) -> str | None:
    if value in (None, ""):
        return value
    return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
