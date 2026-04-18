from __future__ import annotations

from fastapi import HTTPException, status


class ServiceUnavailable(HTTPException):
    def __init__(self, detail: str = "Service temporarily unavailable") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class Forbidden(HTTPException):
    def __init__(self, detail: str = "Insufficient privileges") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class Conflict(HTTPException):
    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
