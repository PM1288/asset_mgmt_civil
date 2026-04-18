from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.security import SubjectContext, auth_subject, require_roles
from app.db.session import get_db


def db_session() -> Session:
    return next(get_db())


def current_subject(subject: SubjectContext = Depends(auth_subject)) -> SubjectContext:
    return subject


def current_admin(subject: SubjectContext = Depends(require_roles("municipal-admin", "operator"))):
    return subject


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
