"""Booking-creation inputs; engineered and outcome fields are forbidden."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

Count = Annotated[int, Field(strict=True, ge=0)]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    hotel: Literal["City Hotel", "Resort Hotel"]
    booking_date: date
    arrival_date: date
    stays_in_weekend_nights: Count
    stays_in_week_nights: Count
    adults: Count
    children: Count | None = None
    babies: Count
    meal: Literal["BB", "FB", "HB", "SC", "Undefined"]
    country: Annotated[str, Field(min_length=1)] | None = None
    market_segment: Literal[
        "Aviation", "Complementary", "Corporate", "Direct", "Groups",
        "Offline TA/TO", "Online TA", "Undefined",
    ]
    distribution_channel: Literal["Corporate", "Direct", "GDS", "TA/TO", "Undefined"]
    is_repeated_guest: StrictBool
    previous_cancellations: Count
    previous_bookings_not_canceled: Count
    reserved_room_type: Literal["A", "B", "C", "D", "E", "F", "G", "H", "L", "P"]
    deposit_type: Literal["No Deposit", "Non Refund", "Refundable"]
    customer_type: Literal["Contract", "Group", "Transient", "Transient-Party"]
    adr: Annotated[float, Field(strict=True, allow_inf_nan=False)]
    required_car_parking_spaces: Count
    total_of_special_requests: Count
    has_agent: StrictBool
    has_company: StrictBool

    @model_validator(mode="after")
    def validate_date_order(self) -> Self:
        if self.arrival_date < self.booking_date:
            raise ValueError("arrival_date must be on or after booking_date")
        return self
