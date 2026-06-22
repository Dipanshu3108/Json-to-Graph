# JSON Viz Studio

JSON-first chart builder with strict validation, AI repair, ECharts rendering, and optional AI-generated full HTML output.

## Stack

- Frontend: Vite + React + TypeScript + Zustand + ECharts + Monaco Editor
- Backend: FastAPI + Pydantic + provider-agnostic LLM wrapper

## Project structure

See the `frontend` and `backend` folders for implementation details.

## Setup

1. Copy `.env.example` to `.env` and fill LLM keys.
2. Backend:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

Frontend runs on `http://localhost:5173` and backend on `http://localhost:8000`.

## Docker

- `docker compose up --build`

## API summary

- `POST /api/validate`
- `POST /api/repair`
- `POST /api/generate-code`
- `GET /health`

All non-2xx responses return `{ "code": "STRING", "message": "Human-readable message" }`.
