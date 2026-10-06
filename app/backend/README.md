# Stage 9: Hotel Cancellation Prediction Backend

FastAPI JSON API for the finalized XGBoost pipeline. It accepts 23 booking-time
business inputs and derives the exact 32 model columns before inference.

## Install and start

Use the project's Python virtual environment. From the repository root:

```powershell
# Windows PowerShell, if the environment is not already activated:
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir app/backend --host 127.0.0.1 --port 8000
```

On macOS/Linux activate with `source .venv/bin/activate`; the Python commands
above are identical. Alternatively, from `app/backend/`, run
`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
Add `--reload` for local development if desired.

Interactive API documentation: <http://127.0.0.1:8000/docs>.

Artifact paths are discovered from the source module's ancestors using
`README.md` and the two model files as markers. No current working directory or
machine-specific absolute path is required for artifact discovery.

The existing ML environment matches the artifact metadata: Python 3.14.6,
pandas 3.0.6, NumPy 2.5.3, scikit-learn 1.9.1, XGBoost 3.4.1, joblib 1.6.0.
The root ML dependencies remain unchanged and unpinned; use the matching
environment when loading this serialized artifact. No installation or startup
step trains or regenerates a model.

## Routes

| Route | Behavior |
|---|---|
| `GET /api/health` | `200` with `status: ok`, `model_loaded: true` when ready; `500` with `status: error`, `model_loaded: false` if loading failed |
| `GET /api/model-info` | Model name, saved threshold, feature count, class labels |
| `POST /api/predict` | Validated booking to cancellation probability and threshold-based class |

Only `http://localhost:5173` and `http://127.0.0.1:5173` are allowed CORS origins.

Example synthetic request for `/api/predict`:

```json
{
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
  "is_repeated_guest": false,
  "previous_cancellations": 0,
  "previous_bookings_not_canceled": 0,
  "reserved_room_type": "A",
  "deposit_type": "No Deposit",
  "customer_type": "Transient",
  "adr": 100.0,
  "required_car_parking_spaces": 0,
  "total_of_special_requests": 1,
  "has_agent": true,
  "has_company": false
}
```

Use ISO `YYYY-MM-DD` dates, nonnegative integer counts, and JSON booleans.
`children` and `country` can be omitted or `null`. Country uses the dataset's
country codes (for example `PRT`); unseen nonempty codes remain supported by
the saved encoder. The documented reservation categories are available as
enums in `/docs`. All other inputs are required.

Zero guests, zero nights, large groups, and finite negative/high ADR are allowed.
No upper limit is inferred from historical training ranges. Arrival before
booking, invalid types/counts/categories, and extra fields return `422`.
Extra-field rejection covers leakage fields, raw agent/company IDs, and
client-supplied engineered values.

## Model and feature contract

Startup loads `models/final_hotel_cancellation_pipeline.joblib` and
`models/final_model_metadata.json` once per application worker/lifespan. Requests
reuse the fitted pipeline. The application never reads any dataset or calls
`fit()`.

The pipeline already contains learned preprocessing and the trained classifier.
Startup verifies its columns, classifier class and probability class order
against metadata. Every prediction verifies a single row of exactly 32 unique,
allowed columns and reorders them using `predictor_columns_in_order`.

- Lead time is arrival minus booking date in days.
- Arrival month uses fixed English names, independent of system locale.
- Arrival week uses Sunday-start weeks with January 1 in week 1, not ISO weeks.
- Missing children count as zero only in guest totals and flags. The original
  missing value reaches the pipeline's fitted children imputer.
- Missing country is represented by `np.nan` in an object column so the fitted
  categorical imputer converts it to `Unknown`.
- Presence/repeat/zero indicators are integers; booking month is an unpadded string.
- Imputation, scaling, and encoding are performed only by the saved pipeline.

Cancellation probability comes from `pipeline.predict_proba(frame)[:, 1]`.
The API applies `probability >= metadata["probability_threshold"]` (currently
`0.33`), without calling `pipeline.predict()`. Classification uses the unrounded
probability; the percentage display is rounded to one decimal place.

The response contains `prediction`, `class`, `cancellation_probability`,
`cancellation_probability_percent`, `threshold`, `model_name`, and a decision
support message. This is an estimate, not a guaranteed reservation outcome.

If startup loading fails, the API remains available with failed health and
controlled `500` responses. Fix the artifacts/environment and restart; requests
do not retry loading. Prediction failures also return a generic `500`. Details
are logged server-side and filesystem paths/stack traces are not returned.

## Run tests

From the repository root with the virtual environment activated:

```powershell
python -m pip install -r app/backend/requirements-test.txt
cd app/backend
python -m unittest discover -s tests -t . -v
```

Tests use `unittest` and FastAPI's HTTPX-backed `TestClient`. Integration tests
load the real saved pipeline and score synthetic bookings. They cover all routes,
validation, missing-value imputation, feature order/formulas, calendar boundaries,
unusual valid bookings, CORS, load-once behavior, and controlled errors.
Only boundary/failure tests replace probability outputs or simulate load errors;
feature engineering is always real. Calendar fixtures were verified against
training date/week pairs during inspection. Tests do not read any dataset.

Implementation references: [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)
and [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/).
