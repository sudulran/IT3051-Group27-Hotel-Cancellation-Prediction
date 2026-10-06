"""FastAPI application with one model load per worker at startup."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import health, prediction
from .config import CORS_ORIGINS
from .ml.model_service import ModelService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.model_service = None
    try:
        application.state.model_service = ModelService()
    except Exception:
        # Keep the API available to report controlled errors and failed health.
        # Restart after repairing artifacts/dependencies; do not reload per request.
        logger.exception("Prediction model could not be initialized")
    try:
        yield
    finally:
        application.state.model_service = None


def create_app() -> FastAPI:
    application = FastAPI(title="Hotel Cancellation Prediction API", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(CORS_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health.router)
    application.include_router(prediction.router)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Do not echo input or exception objects (including non-JSON NaN/Infinity).
        errors = [
            {key: error[key] for key in ("type", "loc", "msg")}
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @application.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled API error", exc_info=(type(exc), exc, exc.__traceback__))
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})

    return application


app = create_app()
