"""Final-system regression checks using synthetic inputs and the saved artifact."""

import ast
from contextlib import ExitStack
import itertools
import json
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from sklearn.pipeline import Pipeline

from app.config import find_repository_root
from app.main import create_app
from app.ml.feature_engineering import engineer_features
from app.ml.model_contract import ModelContract
from app.schemas.prediction import PredictionRequest
from tests import booking_payload, saved_metadata


class InferenceSafetyTests(unittest.TestCase):
    def test_application_has_no_training_or_csv_calls(self):
        source_root = find_repository_root() / "app/backend/app"
        forbidden = {"fit", "fit_transform", "partial_fit", "read_csv"}
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, forbidden, str(path))

    def test_real_requests_do_not_fit_read_csv_or_use_default_predict(self):
        with ExitStack() as stack:
            guards = [
                stack.enter_context(patch(target, side_effect=AssertionError(target)))
                for target in (
                    "pandas.read_csv", "sklearn.pipeline.Pipeline.fit",
                    "sklearn.pipeline.Pipeline.predict",
                )
            ]
            with TestClient(create_app()) as client:
                service = client.app.state.model_service
                self.assertIsInstance(service.pipeline, Pipeline)
                with patch.object(service.pipeline, "predict_proba", wraps=service.pipeline.predict_proba) as scorer:
                    for changes in ({}, {"children": None, "country": None}, {"adr": -6.38}):
                        response = client.post("/api/predict", json=booking_payload(**changes))
                        self.assertEqual(response.status_code, 200, response.text)
                        frame = scorer.call_args.args[0]
                        self.assertEqual(frame.shape, (1, 32))
                        self.assertEqual(list(frame.columns), service.metadata["predictor_columns_in_order"])
                        self.assertIsInstance(frame.at[0, "booking_month"], str)
                        for column in ("has_agent", "has_company"):
                            self.assertTrue(pd.api.types.is_integer_dtype(frame[column]))
                            self.assertIn(frame.at[0, column], (0, 1))
                    self.assertEqual(scorer.call_count, 3)
            for guard in guards:
                guard.assert_not_called()

    def test_derived_features_match_notebook_02_on_synthetic_edge_cases(self):
        path = find_repository_root() / "notebooks/02_Preprocessing_Feature_Engineering.ipynb"
        notebook = json.loads(path.read_text(encoding="utf-8"))
        definitions = []
        for cell in notebook["cells"]:
            source = "".join(cell.get("source", []))
            if cell["cell_type"] == "code" and "def engineer_features(" in source:
                definitions.extend(
                    node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == "engineer_features"
                )
        self.assertEqual(len(definitions), 1)
        # Execute only the pure function definition, never notebook cells,
        # dataset loading, preprocessing fitting or training code.
        namespace = {}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
        notebook_engineer = namespace["engineer_features"]
        contract = ModelContract.from_metadata(saved_metadata())
        derived = ["total_nights", "total_guests", "has_children", "has_agent",
                   "has_company", "is_zero_guest", "is_zero_night", "booking_month"]
        cases = itertools.product(
            (None, 0, 2), (0, 1), (False, True), (False, True),
            (0, 5), ("2016-12-20", "2017-01-08"),
        )
        for children, babies, agent, company, nights, booking_date in cases:
            with self.subTest(children=children, babies=babies, agent=agent, company=company, nights=nights, date=booking_date):
                payload = booking_payload(
                    adults=0, children=children, babies=babies, has_agent=agent,
                    has_company=company, stays_in_weekend_nights=0,
                    stays_in_week_nights=nights, booking_date=booking_date,
                )
                raw = pd.DataFrame([{
                    **payload, "children": np.nan if children is None else children,
                    "booking_date": pd.Timestamp(booking_date),
                    "agent": 123 if agent else np.nan,
                    "company": 456 if company else np.nan,
                }])
                expected = notebook_engineer(raw)
                actual = engineer_features(PredictionRequest(**payload), contract)
                pd.testing.assert_frame_equal(actual[derived], expected[derived], check_dtype=False)
                self.assertEqual(pd.isna(actual.at[0, "children"]), children is None)


if __name__ == "__main__":
    unittest.main()
