"""
Reusable deterministic data preparation for the Hotel Booking
Cancellation Prediction project.

This module reproduces the finalized Stage 4 split and feature-engineering
decisions from 02_Preprocessing_Feature_Engineering.ipynb.

Important:
- It does NOT fit learned preprocessing such as imputers, scalers or encoders.
- Learned preprocessing remains inside the model Pipeline during CV.
- The finalized chronological cutoff is 2017-01-11.
"""

from pathlib import Path

import pandas as pd


TARGET = "is_canceled"

FINAL_CUTOFF_DATE = pd.Timestamp("2017-01-11")

EXPECTED_RAW_ROWS = 119_390
EXPECTED_RAW_COLUMNS = 32

EXPECTED_TRAIN_ROWS = 95_401
EXPECTED_TEST_ROWS = 23_989


COLUMNS_TO_REMOVE = [
    # Direct leakage / later information
    "reservation_status",
    "reservation_status_date",
    "assigned_room_type",
    "booking_changes",
    "days_in_waiting_list",

    # Raw identifier-like fields
    "agent",
    "company",

    # Helper dates used only for splitting / engineering
    "arrival_date",
    "booking_date",
]


EXPECTED_PREDICTORS = [
    "hotel",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "reserved_room_type",
    "deposit_type",
    "customer_type",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "total_nights",
    "total_guests",
    "has_children",
    "has_agent",
    "has_company",
    "is_zero_guest",
    "is_zero_night",
    "booking_month",
]


def add_temporal_helpers(frame):
    """
    Reconstruct arrival_date and booking_date exactly as finalized
    in Notebook 02.
    """

    result = frame.copy()

    result["arrival_date"] = pd.to_datetime(
        result["arrival_date_year"].astype(str)
        + "-"
        + result["arrival_date_month"]
        + "-"
        + result["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d",
    )

    result["booking_date"] = (
        result["arrival_date"]
        - pd.to_timedelta(
            result["lead_time"],
            unit="D",
        )
    )

    return result


def derive_chronological_cutoff(data):
    """
    Reproduce the approximately 80% complete-date chronological cutoff
    used in finalized Notebook 02.
    """

    date_counts = (
        data.groupby("booking_date")
        .size()
        .sort_index()
    )

    cumulative_proportion = (
        date_counts.cumsum() / len(data)
    )

    eligible_dates = cumulative_proportion[
        cumulative_proportion <= 0.80
    ]

    return eligible_dates.index[-1]


def engineer_features(frame):
    """
    Reproduce the finalized deterministic feature engineering
    from Notebook 02.
    """

    result = frame.copy()

    # Used only while constructing derived features.
    # The original children column remains unchanged so that
    # model-pipeline imputation can occur within each CV fold.
    children_for_features = (
        result["children"]
        .fillna(0)
    )

    result["total_nights"] = (
        result["stays_in_weekend_nights"]
        + result["stays_in_week_nights"]
    )

    result["total_guests"] = (
        result["adults"]
        + children_for_features
        + result["babies"]
    )

    result["has_children"] = (
        (
            children_for_features
            + result["babies"]
        ) > 0
    ).astype(int)

    result["has_agent"] = (
        result["agent"].notna()
    ).astype(int)

    result["has_company"] = (
        result["company"].notna()
    ).astype(int)

    result["is_zero_guest"] = (
        result["total_guests"] == 0
    ).astype(int)

    result["is_zero_night"] = (
        result["total_nights"] == 0
    ).astype(int)

    result["booking_month"] = (
        result["booking_date"]
        .dt.month
        .astype(str)
    )

    return result


def prepare_predictors(frame):
    """
    Engineer features and remove finalized leakage, timing-sensitive,
    identifier and helper columns.
    """

    prepared = engineer_features(frame)

    prepared = prepared.drop(
        columns=COLUMNS_TO_REMOVE,
        errors="ignore",
    )

    return prepared


def _load_finalized_raw_data(raw_path):
    """
    Load the approved raw dataset and verify that it still matches
    the dataset used to finalize Stage 4.
    """

    raw_path = Path(raw_path)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_path}"
        )

    data = pd.read_csv(raw_path)

    if data.shape != (
        EXPECTED_RAW_ROWS,
        EXPECTED_RAW_COLUMNS,
    ):
        raise ValueError(
            "Raw dataset does not match the finalized project dataset. "
            f"Expected {(EXPECTED_RAW_ROWS, EXPECTED_RAW_COLUMNS)}, "
            f"found {data.shape}."
        )

    data = add_temporal_helpers(data)

    derived_cutoff = derive_chronological_cutoff(data)

    if derived_cutoff != FINAL_CUTOFF_DATE:
        raise ValueError(
            "Chronological cutoff no longer matches finalized Stage 4. "
            f"Expected {FINAL_CUTOFF_DATE.date()}, "
            f"found {derived_cutoff.date()}."
        )

    return data


def _separate_xy(prepared):
    """
    Separate predictors and target and enforce the finalized
    predictor contract.
    """

    X = prepared.drop(
        columns=[TARGET]
    ).copy()

    y = prepared[
        TARGET
    ].copy()

    if list(X.columns) != EXPECTED_PREDICTORS:
        raise ValueError(
            "Predictor columns/order do not match the finalized "
            "Notebook 02 contract."
        )

    # Keep booking_month explicitly categorical.
    X["booking_month"] = (
        X["booking_month"]
        .astype(str)
    )

    X = X.reset_index(drop=True)
    y = y.reset_index(drop=True)

    return X, y


def prepare_stage4_training_data(raw_path):
    """
    Reproduce ONLY the finalized Stage 4 training partition.

    This is the function Notebook 03 should use.
    The final test partition is not returned.
    """

    data = _load_finalized_raw_data(raw_path)

    train_data = data[
        data["booking_date"] <= FINAL_CUTOFF_DATE
    ].copy()

    if len(train_data) != EXPECTED_TRAIN_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_TRAIN_ROWS:,} training rows, "
            f"found {len(train_data):,}."
        )

    train_prepared = prepare_predictors(
        train_data
    )

    X_train, y_train = _separate_xy(
        train_prepared
    )

    return X_train, y_train


def prepare_stage4_final_test_data(raw_path):
    """
    Reproduce ONLY the finalized Stage 4 final-test partition.

    IMPORTANT:
    Notebook 03 must NOT call this function.

    It is intended for Notebook 04 only AFTER the final model,
    hyperparameters, features, class weighting and threshold
    have been frozen.
    """

    data = _load_finalized_raw_data(raw_path)

    test_data = data[
        data["booking_date"] > FINAL_CUTOFF_DATE
    ].copy()

    if len(test_data) != EXPECTED_TEST_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_TEST_ROWS:,} final-test rows, "
            f"found {len(test_data):,}."
        )

    test_prepared = prepare_predictors(
        test_data
    )

    X_test, y_test = _separate_xy(
        test_prepared
    )

    return X_test, y_test
