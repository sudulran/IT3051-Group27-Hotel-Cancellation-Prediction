"""Read the existing fitted pipeline once per application lifespan."""

import json
from pathlib import Path

import joblib
import numpy as np

from ..config import METADATA_RELATIVE_PATH, MODEL_RELATIVE_PATH, find_repository_root
from ..schemas.prediction import PredictionRequest
from ..schemas.responses import ModelInfoResponse, PredictionResponse
from .feature_engineering import engineer_features
from .model_contract import ModelContract


class ModelService:
    def __init__(self, repository_root: Path | None = None):
        root = repository_root if repository_root is not None else find_repository_root()
        with (root / METADATA_RELATIVE_PATH).open(encoding="utf-8") as source:
            self.metadata = json.load(source)
        self.contract = ModelContract.from_metadata(self.metadata)
        self.pipeline = joblib.load(root / MODEL_RELATIVE_PATH)
        self.contract.validate_pipeline(self.pipeline, self.metadata)

    def model_info(self) -> ModelInfoResponse:
        return ModelInfoResponse(
            model_name=self.contract.model_name,
            threshold=self.contract.threshold,
            feature_count=len(self.contract.columns),
            class_labels=self.metadata["class_labels"],
        )

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        frame = engineer_features(request, self.contract)
        probabilities = np.asarray(self.pipeline.predict_proba(frame))
        if probabilities.shape != (1, 2) or not np.isfinite(probabilities).all():
            raise ValueError("Invalid model probability output.")
        if (probabilities < 0).any() or (probabilities > 1).any():
            raise ValueError("Model probability outside [0, 1].")
        probability = float(probabilities[:, 1][0])
        predicted_class = int(probability >= self.contract.threshold)
        return PredictionResponse(
            prediction=self.metadata["class_labels"][str(predicted_class)],
            predicted_class=predicted_class,
            cancellation_probability=probability,
            cancellation_probability_percent=round(probability * 100, 1),
            threshold=self.contract.threshold,
            model_name=self.contract.model_name,
            message=(
                "This is a model-based estimate for decision support, not a guarantee "
                "that this booking will or will not be cancelled."
            ),
        )
