"""Fail closed if metadata, the saved artifact, or an inference row drifts."""

from dataclasses import dataclass
import math

import pandas as pd

EXPECTED_COLUMNS = (
    "hotel", "lead_time", "arrival_date_year", "arrival_date_month",
    "arrival_date_week_number", "arrival_date_day_of_month",
    "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children",
    "babies", "meal", "country", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "reserved_room_type", "deposit_type", "customer_type", "adr",
    "required_car_parking_spaces", "total_of_special_requests", "total_nights",
    "total_guests", "has_children", "has_agent", "has_company", "is_zero_guest",
    "is_zero_night", "booking_month",
)
FORBIDDEN_COLUMNS = frozenset({
    "reservation_status", "reservation_status_date", "assigned_room_type",
    "booking_changes", "days_in_waiting_list", "agent", "company",
    "is_canceled", "arrival_date", "booking_date",
})


@dataclass(frozen=True)
class ModelContract:
    columns: tuple[str, ...]
    threshold: float
    model_name: str

    @classmethod
    def from_metadata(cls, metadata: dict) -> "ModelContract":
        columns = tuple(metadata["predictor_columns_in_order"])
        if metadata["feature_count"] != 32 or columns != EXPECTED_COLUMNS:
            raise ValueError("Metadata differs from the finalized 32-column contract.")
        threshold = float(metadata["probability_threshold"])
        if not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError("Invalid saved probability threshold.")
        if metadata["class_labels"] != {"0": "Not Cancelled", "1": "Cancelled"}:
            raise ValueError("Unexpected saved class labels.")
        if not isinstance(metadata["model_name"], str) or not metadata["model_name"]:
            raise ValueError("Missing model name.")
        return cls(columns, threshold, metadata["model_name"])

    def validate_pipeline(self, pipeline, metadata: dict) -> None:
        if tuple(pipeline.feature_names_in_) != self.columns:
            raise ValueError("Artifact columns differ from metadata.")
        if list(pipeline.classes_) != [0, 1]:
            raise ValueError("Artifact probability classes are not [0, 1].")
        classifier = pipeline.named_steps["classifier"]
        name = f"{type(classifier).__module__}.{type(classifier).__name__}"
        if name != metadata["model_class"]:
            raise ValueError("Artifact classifier differs from metadata.")
        if not callable(getattr(pipeline, "predict_proba", None)):
            raise ValueError("Artifact does not support probability prediction.")

    def order_and_validate(self, frame: pd.DataFrame) -> pd.DataFrame:
        # Explicit exceptions keep these assertions active under python -O.
        if FORBIDDEN_COLUMNS.intersection(frame.columns):
            raise ValueError("Forbidden model input column.")
        if frame.shape != (1, 32) or not frame.columns.is_unique:
            raise ValueError("Prediction requires one row and exactly 32 unique columns.")
        if set(frame.columns) != set(self.columns):
            raise ValueError("Engineered inputs differ from the model contract.")
        return frame.loc[:, list(self.columns)]
