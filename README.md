# SemiTest AI

SemiTest AI is a simulation-only semiconductor testing and analytics prototype. Physical hardware integration is not implemented or enabled.

## Technology

- Frontend: React, TypeScript, Vite, Tailwind CSS
- Backend: Python, FastAPI, Pydantic, SQLAlchemy
- Database: SQLite
- Tests: Pytest, Vitest, React Testing Library

## Requirements

- Python 3.11 or later
- Node.js 20 or later
- npm

## Setup

From the project root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install -r backend/requirements.txt

cd frontend
npm install
cd ..
```

Use `backend/.venv/bin/python` directly on macOS instead of activating if preferred.

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

The application is forced to `SIMULATION_ONLY`. The SQLite database is created at `backend/data/semitest.db`.

## Run the application

Start the backend from the project root:

```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

In a second terminal, start the frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

The header provides tab navigation for Overview, Devices, Profiles, Testing,
Analytics, Inspection, and System. Each tab opens only its related workspace.
Overview is an executive summary with recent activity and quick actions.
Analytics provides detailed charts and statistical distributions.

## Verify

- Frontend: `http://localhost:5173`
- Backend health: `http://127.0.0.1:8000/api/v1/health`
- Simulation mode: `http://127.0.0.1:8000/api/v1/system/mode`
- Swagger documentation: `http://127.0.0.1:8000/docs`

## Tests

Backend:

```bash
backend/.venv/bin/python -m pytest backend/tests -v
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Phase 1 device APIs

- `POST /api/v1/devices` - register a device
- `GET /api/v1/devices` - list and search devices
- `GET /api/v1/devices/{id}` - retrieve device details
- `PUT /api/v1/devices/{id}` - update or activate/deactivate a device
- `GET /api/v1/devices/{id}/tests` - retrieve test history (returns an empty list until Phase 4 adds test executions)

## Phase 2 test profile APIs

- `POST /api/v1/profiles` - create a profile with measurement definitions
- `GET /api/v1/profiles` - list and filter profiles
- `GET /api/v1/profiles/{id}` - retrieve profile details
- `PUT /api/v1/profiles/{id}` - update a profile and increment its version

## Phase 4 test execution APIs

- `POST /api/v1/tests/execute` - execute a simulation-only test
- `GET /api/v1/tests` - list test executions
- `GET /api/v1/tests/{id}` - retrieve test execution details
- `GET /api/v1/tests/{id}/measurements` - retrieve persisted measurement results

## Phase 5 analytics APIs

- `GET /api/v1/analytics/summary` - overall test counts and pass percentage
- `GET /api/v1/analytics/trends` - test activity over time
- `GET /api/v1/analytics/failures` - failed measurement frequency
- `GET /api/v1/analytics/devices` - device-wise test statistics

## Phase 6 reporting APIs

- `GET /api/v1/reports/{test_id}/pdf` - download a PDF test report
- `GET /api/v1/reports/{test_id}/csv` - download a CSV test report

Reports explicitly identify values as simulated.

## Phase 7 image inspection APIs

- `POST /api/v1/inspections/analyze` - validate, store, resize, and analyze a JPEG or PNG
- `GET /api/v1/inspections/{id}` - retrieve an experimental inspection result

Inspection output is a computer-vision demonstration prediction and requires human review.

## MVP status

Phases 0–8 are implemented. The system remains simulation-only. Real instruments, authenticated enterprise users, and production quality certification are outside this MVP.
