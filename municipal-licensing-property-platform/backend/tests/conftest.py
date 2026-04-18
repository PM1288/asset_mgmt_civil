from __future__ import annotations

import os
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["APP_ENCRYPTION_KEY"] = Fernet.generate_key().decode("utf-8")
os.environ["KEYCLOAK_ISSUER_URL"] = "http://keycloak.local/realms/municipal"

from app.core.config import get_settings  # noqa: E402
from app.core.security import SubjectContext  # noqa: E402
from app.db.base import Base  # noqa: E402

get_settings.cache_clear()

from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)


def override_db():
    from sqlalchemy.orm import Session

    with Session(bind=engine) as session:
        yield session


def override_subject():
    return SubjectContext(
        subject="tester",
        username="tester",
        email="tester@example.local",
        roles={"municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator"},
        token={},
    )


app.dependency_overrides[get_db] = override_db


@pytest.fixture()
def client():
    from app.core.security import auth_subject

    app.dependency_overrides[auth_subject] = override_subject
    with TestClient(app) as test_client:
        yield test_client
