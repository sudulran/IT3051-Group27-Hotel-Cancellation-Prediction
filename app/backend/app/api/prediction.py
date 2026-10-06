"""Model information and validated single-booking predictions."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from ..ml.model_service import ModelService
from ..schemas.prediction import PredictionRequest
from ..schemas.responses import ModelInfoResponse, PredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["prediction"])


def get_model_service(request: Request) -> ModelService:
    service = getattr(request.app.state, "model_service", None)
    if service is None:
        raise HTTPException(status_code=500, detail="Prediction model is unavailable.")
    return service


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(service: Annotated[ModelService, Depends(get_model_service)]) -> ModelInfoResponse:
    return service.model_info()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    booking: PredictionRequest,
    service: Annotated[ModelService, Depends(get_model_service)],
) -> PredictionResponse:
    try:
        return service.predict(booking)
    except Exception:
        logger.exception("Booking prediction failed")
        raise HTTPException(status_code=500, detail="Prediction could not be completed.") from None
