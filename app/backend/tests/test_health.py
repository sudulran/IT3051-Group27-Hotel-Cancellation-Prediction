from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import METADATA_RELATIVE_PATH, MODEL_RELATIVE_PATH, find_repository_root
from app.main import create_app
from tests import booking_payload


class HealthTests(unittest.TestCase):
    def test_health_model_info_and_single_startup_load(self):
        import joblib

        with patch("app.ml.model_service.joblib.load", wraps=joblib.load) as loader:
            with TestClient(create_app()) as client:
                response = client.get("/api/health")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"status": "ok", "model_loaded": True})
                info = client.get("/api/model-info")
                self.assertEqual(info.status_code, 200)
                self.assertEqual(info.json(), {
                    "model_name": "XGBoost", "threshold": 0.33, "feature_count": 32,
                    "class_labels": {"0": "Not Cancelled", "1": "Cancelled"},
                })
                for _ in range(2):
                    self.assertEqual(client.post("/api/predict", json=booking_payload()).status_code, 200)
                loader.assert_called_once()

    def test_load_failure_returns_controlled_errors(self):
        with patch("app.main.ModelService", side_effect=RuntimeError("private/path/model.joblib")):
            with self.assertLogs("app.main", level="ERROR"):
                with TestClient(create_app()) as client:
                    health = client.get("/api/health")
                    self.assertEqual(health.status_code, 500)
                    self.assertEqual(health.json(), {"status": "error", "model_loaded": False})
                    for response in (
                        client.get("/api/model-info"),
                        client.post("/api/predict", json=booking_payload()),
                    ):
                        self.assertEqual(response.status_code, 500)
                        self.assertEqual(response.json(), {"detail": "Prediction model is unavailable."})

    def test_portable_root_detection_from_nested_directory(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for marker in (MODEL_RELATIVE_PATH, METADATA_RELATIVE_PATH, Path("README.md")):
                (root / marker).parent.mkdir(parents=True, exist_ok=True)
                (root / marker).touch()
            nested = root / "app" / "backend" / "app"
            nested.mkdir(parents=True)
            self.assertEqual(find_repository_root(nested), root.resolve())
            (root / METADATA_RELATIVE_PATH).unlink()
            with self.assertRaises(FileNotFoundError):
                find_repository_root(nested)


if __name__ == "__main__":
    unittest.main()
