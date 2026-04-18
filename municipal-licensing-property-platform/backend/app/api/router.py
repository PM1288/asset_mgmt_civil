from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import admin, auth, documents, health, licenses, properties, workflows

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(properties.router)
api_router.include_router(licenses.router)
api_router.include_router(workflows.router)
api_router.include_router(documents.router)
api_router.include_router(admin.router)

system_router = APIRouter()
system_router.include_router(health.router)
