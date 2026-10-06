"""Readiness endpoint."""

from fastapi import APIRouter, Request, Response

from ..schemas.responses import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request, response: Response) -> HealthResponse:
    loaded = getattr(request.app.state, "model_service", None) is not None
    if not loaded:
        response.status_code = 500
    return HealthResponse(status="ok" if loaded else "error", model_loaded=loaded)
