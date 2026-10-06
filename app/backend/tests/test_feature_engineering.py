from datetime import date
import unittest

import pandas as pd

from app.ml.feature_engineering import arrival_week_number, engineer_features
from app.ml.model_contract import ModelContract
from app.schemas.prediction import PredictionRequest
from tests import booking_payload, saved_metadata


class FeatureEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = saved_metadata()
        cls.contract = ModelContract.from_metadata(cls.metadata)

    def frame(self, **overrides):
        return engineer_features(PredictionRequest(**booking_payload(**overrides)), self.contract)

    def test_complete_engineered_row_and_metadata_column_order(self):
        frame = self.frame()
        self.assertEqual(frame.shape, (1, 32))
        self.assertEqual(list(frame.columns), self.metadata["predictor_columns_in_order"])
        expected = {
            "hotel": "City Hotel", "lead_time": 19, "arrival_date_year": 2017,
            "arrival_date_month": "January", "arrival_date_week_number": 2,
            "arrival_date_day_of_month": 8, "stays_in_weekend_nights": 2,
            "stays_in_week_nights": 3, "adults": 2, "children": 1, "babies": 1,
            "meal": "BB", "country": "PRT", "market_segment": "Online TA",
            "distribution_channel": "TA/TO", "is_repeated_guest": 0,
            "previous_cancellations": 0, "previous_bookings_not_canceled": 0,
            "reserved_room_type": "A", "deposit_type": "No Deposit",
            "customer_type": "Transient", "adr": 100.0,
            "required_car_parking_spaces": 0, "total_of_special_requests": 1,
            "total_nights": 5, "total_guests": 4, "has_children": 1,
            "has_agent": 1, "has_company": 0, "is_zero_guest": 0,
            "is_zero_night": 0, "booking_month": "12",
        }
        self.assertEqual(frame.iloc[0].to_dict(), expected)

    def test_missing_children_and_country_preserve_imputation(self):
        row = self.frame(children=None, country=None, babies=0).iloc[0]
        self.assertTrue(pd.isna(row["children"]))
        self.assertTrue(pd.isna(row["country"]))
        self.assertEqual(row["total_guests"], 2)
        self.assertEqual(row["has_children"], 0)

    def test_babies_count_as_children_even_when_children_missing(self):
        row = self.frame(children=None, babies=1).iloc[0]
        self.assertEqual(row["total_guests"], 3)
        self.assertEqual(row["has_children"], 1)

    def test_presence_and_repeat_flags(self):
        for agent in (False, True):
            for company in (False, True):
                with self.subTest(agent=agent, company=company):
                    row = self.frame(has_agent=agent, has_company=company, is_repeated_guest=True).iloc[0]
                    self.assertEqual(row["has_agent"], int(agent))
                    self.assertEqual(row["has_company"], int(company))
                    self.assertEqual(row["is_repeated_guest"], 1)

    def test_zero_guests_and_zero_nights(self):
        row = self.frame(
            adults=0, children=None, babies=0,
            stays_in_weekend_nights=0, stays_in_week_nights=0,
        ).iloc[0]
        for column in ("total_nights", "total_guests", "has_children"):
            self.assertEqual(row[column], 0)
        self.assertEqual(row["is_zero_guest"], 1)
        self.assertEqual(row["is_zero_night"], 1)

    def test_same_day_booking_and_unpadded_booking_month(self):
        row = self.frame(booking_date="2017-01-08").iloc[0]
        self.assertEqual(row["lead_time"], 0)
        self.assertEqual(row["booking_month"], "1")

    def test_week_numbers_verified_against_training_convention(self):
        # Fixed date/week pairs checked in X_train_engineered.csv during inspection.
        # The test suite does not open any dataset.
        examples = {
            "2015-07-04": 27, "2015-07-05": 28,
            "2016-01-01": 1, "2016-01-03": 2, "2016-02-29": 10,
            "2016-12-31": 53, "2017-01-01": 1,
            "2017-01-07": 1, "2017-01-08": 2,
        }
        for value, expected in examples.items():
            with self.subTest(date=value):
                self.assertEqual(arrival_week_number(date.fromisoformat(value)), expected)

    def test_contract_reorders_and_rejects_invalid_frames(self):
        frame = self.frame()
        pd.testing.assert_frame_equal(
            self.contract.order_and_validate(frame.iloc[:, ::-1]), frame,
        )
        for invalid in (
            frame.drop(columns="hotel"),
            frame.assign(reservation_status="Canceled"),
            frame.rename(columns={"hotel": "reservation_status"}),
            frame.rename(columns={"hotel": "unexpected"}),
            pd.concat([frame, frame]),
            frame.rename(columns={"hotel": "lead_time"}),
        ):
            with self.subTest(columns=list(invalid.columns)):
                with self.assertRaises(ValueError):
                    self.contract.order_and_validate(invalid)

    def test_metadata_drift_is_rejected(self):
        for changes in (
            {"predictor_columns_in_order": list(reversed(self.contract.columns))},
            {"feature_count": 31}, {"probability_threshold": float("nan")},
            {"probability_threshold": 1.5},
            {"class_labels": {"0": "Cancelled", "1": "Not Cancelled"}},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    ModelContract.from_metadata({**self.metadata, **changes})


if __name__ == "__main__":
    unittest.main()
