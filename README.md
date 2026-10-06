# Hotel Booking Cancellation Prediction

**Module:** IT3051 – Fundamentals of Data Mining  
**Group:** Group 27 – Entropy Zero  
**Task:** Binary Classification

## Problem

Predict whether an individual hotel reservation will be cancelled before the final booking outcome is known.

## Target Variable

`is_canceled`

- `0` = Not Cancelled
- `1` = Cancelled

## Dataset

Hotel Booking Demand Dataset

- 119,390 records
- 32 columns
- City Hotel and Resort Hotel bookings
- Original source: Antonio, N., de Almeida, A., & Nunes, L. (2019), *Hotel booking demand datasets*, Data in Brief, 22, 41–49.
- DOI: 10.1016/j.dib.2018.11.126

The raw dataset should remain unchanged.

## Notebook Workflow

1. `01_Data_Understanding_EDA.ipynb`
2. `02_Preprocessing_Feature_Engineering.ipynb`
3. `03_Model_Development_Comparison.ipynb`
4. `04_Model_Optimization_Final_Evaluation.ipynb`

## Run the Final System Locally

### Prerequisites

- Install a supported **Node.js LTS** release normally from
  [nodejs.org](https://nodejs.org/en/download) (Node.js 24 LTS is recommended).
  Open a new terminal and verify both `node --version` and `npm --version`
  work on PATH. The project does not depend on a temporary Node installation.
- Use the project Python environment. The saved model was produced with
  **Python 3.14.6**, pandas 3.0.6, NumPy 2.5.3, scikit-learn 1.9.1,
  XGBoost 3.4.1 and joblib 1.6.0. The setup command below preserves these
  serialized-model dependency versions rather than upgrading them implicitly.
- Keep these existing files in the repository:
  `models/final_hotel_cancellation_pipeline.joblib` and
  `models/final_model_metadata.json`. Neither datasets nor notebook execution
  are needed to start the application. Do not retrain to start the system.

Use two terminals. The following commands assume Windows PowerShell and start
from the repository root.

### Terminal 1: backend (port 8000)

```powershell
python --version
# Only if the repository does not already have a .venv:
python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt pandas==3.0.6 numpy==2.5.3 scikit-learn==1.9.1 xgboost==3.4.1 joblib==1.6.0
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir app/backend --host 127.0.0.1 --port 8000
```

### Terminal 2: frontend (port 5173)

```powershell
node --version
npm --version
cd app/frontend
npm ci
npm run dev
```

On macOS/Linux, use `.venv/bin/python` instead of `.\.venv\Scripts\python.exe`;
the npm commands are the same. If PowerShell blocks `npm.ps1`, use `npm.cmd`
for the same commands; no execution-policy change is required.

| Purpose | URL |
|---|---|
| Frontend | http://localhost:5173 (or http://127.0.0.1:5173) |
| Backend health | http://127.0.0.1:8000/api/health |
| Model information | http://127.0.0.1:8000/api/model-info |
| Interactive API documentation | http://127.0.0.1:8000/docs |

A healthy backend reports `{"status":"ok","model_loaded":true}`. The
prediction route is `POST /api/predict`; the frontend sends JSON to this route.
Vite is configured with `port: 5173` and `strictPort: true`. Stop the process
occupying that port if startup fails; do not silently switch frontend ports.
The backend permits only the two local frontend origins in the table through
CORS.

The frontend defaults to `http://127.0.0.1:8000` for the API. To override it,
copy `app/frontend/.env.example` to `app/frontend/.env.local` and set
`VITE_API_BASE_URL`. Restart Vite after changes; production builds need to be
rebuilt. This variable is public configuration, not a place for secrets.
An API port change must also be reflected in the Uvicorn command. Serving the
frontend on another origin requires an explicit backend CORS configuration.

### System architecture

```text
React booking form (23 business inputs)
  -> centralized JSON API client
  -> POST /api/predict (FastAPI)
  -> Pydantic validation (unexpected fields rejected)
  -> deterministic Stage 4 feature engineering
  -> one-row DataFrame: exactly 32 columns in metadata order
  -> saved fitted Pipeline: preprocessing + XGBoost
  -> predict_proba()[:, 1]
  -> probability >= metadata probability_threshold (currently 0.33)
  -> JSON label + probability + decision-support message
  -> React result card and probability meter
```

Each backend worker loads the saved pipeline and metadata once at startup.
Normal predictions do not load training/final-test CSVs or call `fit()` or
the pipeline's default `predict()`. The model contract is documented in
[docs/model_input_schema.md](docs/model_input_schema.md).

Date handling uses English month names, a string booking month and the
dataset-compatible Sunday-based arrival week (January 1 belongs to week 1),
not ISO weeks. Missing children count as zero only for derived guest features;
their missing value is preserved for fitted imputation. Agent/company inputs
are presence booleans converted to 0/1. Leakage fields and raw agent/company
IDs are rejected. Zero guests, zero nights, large groups, and finite
negative/high ADR remain valid.

### Verification

Backend, from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r app/backend/requirements-test.txt
cd app/backend
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
```

Frontend, from `app/frontend/`:

```powershell
npm run lint
npm run build
npx playwright install chromium
npm test
npm run test:integration
```

Stop local servers before browser tests: tests reserve ports 5173 and, for the
integration suite, 8000. `npm test` covers controlled loading/error/result
states. `npm run test:integration` starts both actual servers, checks the live
JSON schema, and scores synthetic bookings through the saved model at desktop
and mobile widths without mocking predictions. It uses the repository `.venv`
or Python on PATH; `PYTHON_EXECUTABLE` can select another compatible interpreter.
Test servers shut down when the suite finishes.

Backend tests also compare the isolated pure feature-engineering function from
Notebook 02 with the backend on synthetic edge cases. No modelling notebook is
executed end-to-end, changed or trained by these checks. No dataset is read.

### Limitations and troubleshooting

- A model-loading failure produces failed health and controlled 500 responses.
  Check that both artifacts exist and the Python/ML versions match metadata,
  inspect the backend terminal, then restart. No stack trace is sent to the UI.
- If the UI cannot connect, confirm backend health, `VITE_API_BASE_URL` and the
  exact allowed frontend origin. Input errors return 422 with field details.
- Root ML requirements remain unpinned; use the version-constrained setup
  command above for this artifact. The frontend lockfile is used by `npm ci`.
- The current backend test client emits an HTTPX deprecation warning; this is
  separate from prediction behavior and does not fail the tests.
- Browser automation covers Chromium. Screen-reader behavior and other browser
  engines have not been fully audited. Predictions are decision support; the
  historical two-hotel dataset does not guarantee performance for current or
  different properties.

See [backend documentation](app/backend/README.md) and
[frontend documentation](app/frontend/README.md) for additional details.

