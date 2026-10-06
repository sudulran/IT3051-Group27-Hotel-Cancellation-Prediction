"""Pure Stage 4 inference transformations; no dataset access or fitting."""

from datetime import date

import numpy as np
import pandas as pd

from ..schemas.prediction import PredictionRequest
from .model_contract import ModelContract

ENGLISH_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def arrival_week_number(arrival_date: date) -> int:
    """Sunday-start week, with the week containing January 1 numbered 1."""
    jan_1 = date(arrival_date.year, 1, 1)
    sunday_based_offset = (jan_1.weekday() + 1) % 7
    return ((arrival_date.timetuple().tm_yday + sunday_based_offset - 1) // 7) + 1


def engineer_features(request: PredictionRequest, contract: ModelContract) -> pd.DataFrame:
    row = request.model_dump(exclude={"booking_date", "arrival_date"})
    children_for_features = 0 if request.children is None else request.children
    total_nights = request.stays_in_weekend_nights + request.stays_in_week_nights
    total_guests = request.adults + children_for_features + request.babies
    row.update({
        "lead_time": (request.arrival_date - request.booking_date).days,
        "arrival_date_year": request.arrival_date.year,
        "arrival_date_month": ENGLISH_MONTHS[request.arrival_date.month - 1],
        "arrival_date_day_of_month": request.arrival_date.day,
        "arrival_date_week_number": arrival_week_number(request.arrival_date),
        "total_nights": total_nights,
        "total_guests": total_guests,
        "has_children": int(children_for_features + request.babies > 0),
        "has_agent": int(request.has_agent),
        "has_company": int(request.has_company),
        "is_repeated_guest": int(request.is_repeated_guest),
        "is_zero_guest": int(total_guests == 0),
        "is_zero_night": int(total_nights == 0),
        "booking_month": str(request.booking_date.month),
        "children": np.nan if request.children is None else request.children,
        "country": np.nan if request.country is None else request.country,
    })
    frame = pd.DataFrame([row])
    # Explicit object dtype preserves np.nan for the fitted categorical imputer,
    # including with pandas versions that infer a dedicated string dtype.
    frame["country"] = pd.Series([row["country"]], dtype=object)
    return contract.order_and_validate(frame)
