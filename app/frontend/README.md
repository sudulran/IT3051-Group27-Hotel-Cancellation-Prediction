# Stage 10: Hotel Cancellation Risk Predictor

React + Vite + Tailwind CSS frontend for the existing Stage 9 FastAPI API.
Application code is JavaScript. All HTTP requests live in
`src/api/predictionApi.js`.

## Start locally

Install a supported Node.js LTS release normally (Node.js 24 LTS recommended)
with npm. Verify `node --version` and `npm --version` on PATH in a new terminal.
No temporary runtime path is required by the project.
Use two terminals, starting from the repository root.

Backend (Windows PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir app/backend --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd app/frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite uses `port: 5173` and `strictPort: true`;
an occupied port causes startup to fail rather than switching ports. Only
localhost and 127.0.0.1 on port 5173 are permitted by the backend's local CORS
configuration. `npm run preview` also uses port 5173.

The default API base URL is `http://127.0.0.1:8000`. To change it, copy
`.env.example` to `.env.local`, edit `VITE_API_BASE_URL`, and restart Vite.
Vite environment values are public browser configuration, not secret storage.
Production builds read them at build time. Deployments on another frontend
origin need a corresponding explicit backend CORS configuration.

## Checks

```powershell
npm run lint
npm run build
npx playwright install chromium
npm test
npm run test:integration
```

Browser tests start their own Vite server on port 5173, so stop the dev server
first. These UI tests use controlled API responses to check payloads, results,
validation, loading, failure states and responsive layout. Normal application
requests go to the real backend. Backend real-model integration tests remain
under `app/backend/tests/`.

The separate integration suite starts the real FastAPI backend on port 8000
and Vite on 5173. Stop both local servers first. It checks the live request
schema and scores synthetic bookings through the saved model at desktop and
mobile widths, including missing values and unusual valid records. It uses
the repository `.venv` when present, otherwise Python on PATH. Set
`PYTHON_EXECUTABLE` if another compatible interpreter is needed. No model
prediction is mocked in this suite.

## Interface and contract

- Five grouped form sections collect only the 23 booking-time API fields.
- Known categories match the Pydantic schema; the searchable country list uses
  English names and submits three-letter codes. Unknown country and blank
  children submit `null`.
- Numeric fields submit JSON numbers, and presence/repeat fields submit JSON
  booleans. ADR accepts finite negative values. Zero guests/nights and large
  counts are supported.
- Booking date defaults to today in the browser's local calendar. Arrival date
  cannot precede booking date. The backend remains authoritative for validation.
- Results use the backend's class label and probability. The frontend does not
  recompute classification, engineer model features or invent explanations.
- Editing a booking clears its old result. Pending requests disable editing
  and repeat submission. Clear / New Prediction resets the form and focuses
  Hotel Type.
- Field errors and connection/server failures appear in an accessible alert.
  Requests time out after 30 seconds; server stack traces are never displayed.
- Labels, native inputs, visible focus, an accessible probability meter and
  text outcomes support keyboard and screen-reader use. No motion is needed.

Tailwind v4 uses the official `@tailwindcss/vite` plugin and
`@import "tailwindcss"`, following the
[Tailwind Vite integration](https://tailwindcss.com/docs/installation/using-vite).
There is no v3 PostCSS/configuration setup. Dependency versions are recorded
in `package-lock.json`; no model files or notebooks are needed in the browser.
