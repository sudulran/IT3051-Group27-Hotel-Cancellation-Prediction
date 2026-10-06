"""Portable artifact discovery and local frontend configuration."""

from pathlib import Path

MODEL_RELATIVE_PATH = Path("models/final_hotel_cancellation_pipeline.joblib")
METADATA_RELATIVE_PATH = Path("models/final_model_metadata.json")
CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def find_repository_root(start: Path | None = None) -> Path:
    """Search ancestors of this module, independent of the launch directory."""
    location = Path(start) if start is not None else Path(__file__)
    location = location.resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if all(
            (candidate / marker).is_file()
            for marker in (MODEL_RELATIVE_PATH, METADATA_RELATIVE_PATH, Path("README.md"))
        ):
            return candidate
    raise FileNotFoundError("Repository model artifacts could not be located.")
