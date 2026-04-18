from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import SubjectContext, auth_subject

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(subject: SubjectContext = Depends(auth_subject)) -> dict:
    return {
        "subject": subject.subject,
        "username": subject.username,
        "email": subject.email,
        "roles": sorted(subject.roles),
    }
