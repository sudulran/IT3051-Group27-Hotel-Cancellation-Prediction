"""Public response fields; filesystem and training internals stay private."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "error"]
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    threshold: float
    feature_count: int
    class_labels: dict[str, str]


class PredictionResponse(BaseModel):
    prediction: Literal["Cancelled", "Not Cancelled"]
    predicted_class: Literal[0, 1] = Field(serialization_alias="class")
    cancellation_probability: float = Field(ge=0, le=1)
    cancellation_probability_percent: float = Field(ge=0, le=100)
    threshold: float
    model_name: str
    message: str
