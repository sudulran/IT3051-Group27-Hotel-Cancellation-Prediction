import unittest
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient

from app.main import create_app
from app.ml.feature_engineering import engineer_features
from app.schemas.prediction import PredictionRequest
from tests import booking_payload


class PredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = create_app()
        cls.client = TestClient(cls.application)
        cls.client.__enter__()
        cls.addClassCleanup(cls.client.__exit__, None, None, None)
        cls.service = cls.application.state.model_service
        if cls.service is None:
            raise RuntimeError("Real saved artifact must load for integration tests.")

    def test_valid_prediction_with_real_saved_pipeline(self):
        response = self.client.post("/api/predict", json=booking_payload())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(set(result), {
            "prediction", "class", "cancellation_probability",
            "cancellation_probability_percent", "threshold", "model_name", "message",
        })
        frame = engineer_features(PredictionRequest(**booking_payload()), self.service.contract)
        expected_probability = float(self.service.pipeline.predict_proba(frame)[:, 1][0])
        self.assertAlmostEqual(result["cancellation_probability"], expected_probability)
        self.assertEqual(result["threshold"], self.service.metadata["probability_threshold"])
        self.assertEqual(result["class"], int(expected_probability >= result["threshold"]))
        self.assertEqual(result["prediction"], self.service.metadata["class_labels"][str(result["class"])])
        self.assertEqual(result["cancellation_probability_percent"], round(expected_probability * 100, 1))
        self.assertIn("decision support", result["message"])

    def test_missing_optional_values_with_real_pipeline(self):
        for omit in (False, True):
            with self.subTest(omit=omit):
                payload = booking_payload(children=None, country=None)
                if omit:
                    del payload["children"]
                    del payload["country"]
                response = self.client.post("/api/predict", json=payload)
                self.assertEqual(response.status_code, 200, response.text)
                frame = engineer_features(PredictionRequest(**payload), self.service.contract)
                categorical = self.service.pipeline.named_steps["preprocessor"].named_transformers_["categorical"]
                imputed = categorical.named_steps["imputer"].transform(
                    frame[self.service.metadata["categorical_columns"]]
                )
                country_index = self.service.metadata["categorical_columns"].index("country")
                self.assertEqual(imputed[0, country_index], "Unknown")

    def test_arrival_before_booking_rejected(self):
        response = self.client.post("/api/predict", json=booking_payload(arrival_date="2016-12-19"))
        self.assertEqual(response.status_code, 422)
        self.assertIn("arrival_date must be on or after booking_date", response.text)

    def test_forbidden_and_unexpected_fields_rejected(self):
        for field in (
            "reservation_status", "reservation_status_date", "assigned_room_type",
            "booking_changes", "days_in_waiting_list", "agent", "company",
            "is_canceled", "total_guests", "lead_time", "unexpected",
        ):
            with self.subTest(field=field):
                response = self.client.post("/api/predict", json=booking_payload(**{field: "forbidden"}))
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["detail"][0]["type"], "extra_forbidden")

    def test_invalid_types_and_ranges_return_422(self):
        for changes in (
            {"adults": -1}, {"adults": 1.5}, {"adults": True},
            {"children": -1}, {"stays_in_week_nights": -1},
            {"has_agent": "yes"}, {"country": "   "},
            {"arrival_date": "2017-02-30"}, {"adr": "Infinity"},
            {"adr": True}, {"hotel": "Unknown hotel"},
        ):
            with self.subTest(changes=changes):
                response = self.client.post("/api/predict", json=booking_payload(**changes))
                self.assertEqual(response.status_code, 422, response.text)

    def test_integer_and_decimal_adr_numbers_with_real_pipeline(self):
        for value in (100, 100.0, 123.45, -6.38, 10000):
            with self.subTest(adr=value, number_type=type(value).__name__):
                response = self.client.post("/api/predict", json=booking_payload(adr=value))
                self.assertEqual(response.status_code, 200, response.text)

    def test_boolean_string_and_nonnumeric_adr_rejected(self):
        for value in (True, False, "100", "123.45", "NaN", "Infinity", "invalid", None, [], {}):
            with self.subTest(adr=value):
                response = self.client.post("/api/predict", json=booking_payload(adr=value))
                self.assertEqual(response.status_code, 422, response.text)
                self.assertTrue(any(
                    error["loc"] == ["body", "adr"]
                    for error in response.json()["detail"]
                ))

    def test_nonfinite_adr_returns_controlled_validation_error(self):
        import json

        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value):
                response = self.client.post(
                    "/api/predict", content=json.dumps(booking_payload(adr=value)),
                    headers={"Content-Type": "application/json"},
                )
                self.assertEqual(response.status_code, 422, response.text)

    def test_unusual_valid_bookings_remain_supported(self):
        for changes in (
            {"adults": 0, "children": 0, "babies": 0},
            {"stays_in_weekend_nights": 0, "stays_in_week_nights": 0},
            {"adults": 100}, {"adr": -6.38}, {"adr": 10000.0},
        ):
            with self.subTest(changes=changes):
                response = self.client.post("/api/predict", json=booking_payload(**changes))
                self.assertEqual(response.status_code, 200, response.text)

    def test_saved_threshold_boundary_and_no_default_predict(self):
        threshold = self.service.contract.threshold
        for probability, expected in ((threshold - 0.000001, 0), (threshold, 1), (0.4, 1)):
            with self.subTest(probability=probability):
                # Only control model output to exercise exact threshold boundaries;
                # request validation and real feature engineering still execute.
                with patch.object(self.service.pipeline, "predict_proba", return_value=np.array([[1 - probability, probability]])) as predict_proba:
                    with patch.object(self.service.pipeline, "predict", side_effect=AssertionError("Must use probabilities")) as predict:
                        response = self.client.post("/api/predict", json=booking_payload())
                        self.assertEqual(response.status_code, 200, response.text)
                        self.assertEqual(response.json()["class"], expected)
                        predict.assert_not_called()
                        frame = predict_proba.call_args.args[0]
                        self.assertEqual(frame.shape, (1, 32))
                        self.assertEqual(list(frame.columns), self.service.metadata["predictor_columns_in_order"])

    def test_prediction_failure_returns_controlled_500(self):
        with patch.object(self.service.pipeline, "predict_proba", side_effect=RuntimeError("private/path")):
            with self.assertLogs("app.api.prediction", level="ERROR"):
                response = self.client.post("/api/predict", json=booking_payload())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Prediction could not be completed."})

    def test_invalid_model_probabilities_return_controlled_500(self):
        for output in (np.array([[np.nan, np.nan]]), np.array([[0.1, 1.1]]), np.array([0.4])):
            with self.subTest(output=output):
                with patch.object(self.service.pipeline, "predict_proba", return_value=output):
                    with self.assertLogs("app.api.prediction", level="ERROR"):
                        response = self.client.post("/api/predict", json=booking_payload())
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.json(), {"detail": "Prediction could not be completed."})

    def test_cors_only_allows_local_vite_origins(self):
        for origin in ("http://localhost:5173", "http://127.0.0.1:5173", "https://untrusted.example"):
            with self.subTest(origin=origin):
                response = self.client.options("/api/predict", headers={
                    "Origin": origin, "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                })
                if origin.endswith(":5173"):
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.headers["access-control-allow-origin"], origin)
                else:
                    self.assertEqual(response.status_code, 400)
                    self.assertNotIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":
    unittest.main()
