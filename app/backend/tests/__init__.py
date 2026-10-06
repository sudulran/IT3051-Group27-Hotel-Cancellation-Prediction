"""Synthetic booking fixtures; no training or final-test dataset is read."""

import json

from app.config import METADATA_RELATIVE_PATH, find_repository_root


def booking_payload(**overrides):
    payload = {
        "hotel": "City Hotel",
        "booking_date": "2016-12-20",
        "arrival_date": "2017-01-08",
        "stays_in_weekend_nights": 2,
        "stays_in_week_nights": 3,
        "adults": 2,
        "children": 1,
        "babies": 1,
        "meal": "BB",
        "country": "PRT",
        "market_segment": "Online TA",
        "distribution_channel": "TA/TO",
        "is_repeated_guest": False,
        "previous_cancellations": 0,
        "previous_bookings_not_canceled": 0,
        "reserved_room_type": "A",
        "deposit_type": "No Deposit",
        "customer_type": "Transient",
        "adr": 100.0,
        "required_car_parking_spaces": 0,
        "total_of_special_requests": 1,
        "has_agent": True,
        "has_company": False,
    }
    payload.update(overrides)
    return payload


def saved_metadata():
    return json.loads((find_repository_root() / METADATA_RELATIVE_PATH).read_text(encoding="utf-8"))
