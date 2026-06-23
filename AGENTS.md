# JSON Viz Studio — Agent Guide

This file is written for AI coding agents working on **JSON Viz Studio**, a JSON-first chart builder. It combines strict server-side validation, optional AI repair, local ECharts rendering, and optional LLM-generated full HTML output.

If you edit anything related to the stack, conventions, or processes described here, keep this file up to date.

---

## Project Overview

JSON Viz Studio is a full-stack web application with two independently runnable parts:

- **Frontend** — Vite + React + TypeScript SPA. Users paste JSON, pick a chart type/theme, and see either a live ECharts preview or an LLM-generated self-contained HTML preview rendered in a sandboxed iframe.
- **Backend** — FastAPI service that validates/repairs chart JSON and can ask an LLM to generate complete chart HTML.

The project supports six chart types: `bar`, `line`, `area`, `pie`, `doughnut`, `scatter`.

### Repository Layout

```
.
├── .env.example
├── docker-compose.yml
├── README.md
├── requirements.txt            # (legacy) streamlit/genai/pydantic
├── ollama/                     # (legacy) Ollama setup; no longer used by default
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt        # fastapi, uvicorn, pydantic, httpx, pytest
│   ├── app/
│   │   ├── main.py             # FastAPI app, CORS, routers, /health
│   │   ├── api/                # route handlers
│   │   │   ├── validate.py
│   │   │   ├── repair.py
│   │   │   └── generate_code.py
│   │   ├── schemas/
│   │   │   └── chart.py        # Pydantic request/response models
│   │   ├── services/           # business logic
│   │   │   ├── llm_service.py  # provider-agnostic LLM client
│   │   │   ├── normalizer.py   # key-alias normalization
│   │   │   ├── repair_prompt.py # per-chart-type prompt builder
│   │   │   ├── sandbox.py      # regex-based HTML sanitisation
│   │   │   └── validator.py    # schema validation
│   │   └── prompts/            # system prompt templates
│   │       ├── repair_schema.txt
│   │       └── generate_chart_code.txt
│   └── tests/
│       ├── test_llm_service.py
│       ├── test_normalizer.py
│       └── test_validator.py
└── frontend/
    ├── Dockerfile
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── styles.css
        ├── components/
        │   ├── ChartPreview.tsx
        │   ├── ChartTypeSelector.tsx
        │   ├── CodePreview.tsx
        │   ├── ErrorBoundary.tsx
        │   ├── JsonEditor.tsx
        │   ├── StatusBar.tsx
        │   └── ThemeSelector.tsx
        ├── hooks/
        │   ├── useChartConfig.ts
        │   └── useValidate.ts
        ├── services/
        │   └── api.ts
        ├── store/
        │   └── useStudioStore.ts
        ├── types/
        │   └── index.ts
        └── utils/
            ├── colorPalette.ts
            ├── schemaValidator.ts
            └── chartConfigBuilders/
                ├── area.ts
                ├── bar.ts
                ├── doughnut.ts
                ├── line.ts
                ├── pie.ts
                └── scatter.ts
```

---

## Technology Stack

### Backend

- **Runtime / Language**: Python 3.12
- **Framework**: FastAPI 0.115.2
- **Server**: Uvicorn 0.30.6
- **Validation**: Pydantic 2.9.2
- **HTTP client**: httpx 0.27.2
- **LLM provider**: Kimi (Moonshot AI)
- **Testing**: pytest 8.3.3

### Frontend

- **Build tool**: Vite 5.4.8
- **Framework**: React 18.3.1 + TypeScript 5.6.2
- **State management**: Zustand 4.5.5
- **Charts**: Apache ECharts 5.5.1 (tree-shaken imports)
- **Editor**: Monaco Editor via `@monaco-editor/react`
- **Testing**: Vitest 2.1.1 (no tests currently checked in under `src/`)

### Infrastructure

- Docker and Docker Compose for local containerised runs.
- Separate `Dockerfile`s in `backend/` and `frontend/`.
- Environment configuration via `.env` (see `.env.example`).

---

## Configuration

Copy `.env.example` to `.env` and fill in your Kimi API key.

Key variables:

| Variable | Purpose |
| --- | --- |
| `MOONSHOT_API_KEY` | Kimi (Moonshot AI) API key. |
| `LLM_MODEL_KIMI` | Kimi model name (default: `kimi-k2.6`). |
| `KIMI_BASE_URL` | Kimi API base URL (default: `https://api.moonshot.ai/v1`). |
| `LLM_TIMEOUT_SECONDS` | Request timeout (default: `120`). |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins. |
| `VITE_API_BASE_URL` | Frontend build-time variable pointing to the backend. |

The frontend uses `import.meta.env.VITE_API_BASE_URL` at build time only.

---

## Build and Run Commands

### Local Development

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

- Frontend URL: `http://localhost:5173`
- Backend URL: `http://localhost:8000`
- Health check: `GET http://localhost:8000/health`

### Docker

```bash
docker compose up --build
```

This builds and starts three services:

- `backend` — configured to call Kimi using the credentials in `.env`.
- `frontend` — runs Vite dev mode, forcing `--host 0.0.0.0` and overriding `VITE_API_BASE_URL` to `http://localhost:8000`.

Exposed ports: `8000` (backend), `5173` (frontend).

### Production Build (Frontend)

```bash
cd frontend
npm run build
```

Runs TypeScript compilation (`tsc -b`) and Vite production build. Output lands in `frontend/dist/`. Preview it with `npm run preview`.

---

## API Reference

All routes are included by `app/main.py` without a prefix. Error responses follow `{ code: string, message: string }`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe. Returns `{ "status": "ok" }`. |
| `POST` | `/api/validate` | Validates and normalises chart JSON. |
| `POST` | `/api/repair` | Builds a per-chart-type prompt from the invalid input, sends it to the configured LLM, and re-validates the result. |
| `POST` | `/api/generate-code` | Asks the LLM for a complete self-contained HTML file rendering the chart. |

### Request/Response Schemas

Defined in `backend/app/schemas/chart.py`:

- `ValidateRequest`: `{ chartType: ChartTypeStr, data: dict }`
- `ValidateResponse`: `{ valid: bool, errors: list[dict], normalizedData: dict | null }`
- `RepairRequest`: `{ chartType: ChartTypeStr, data: Any }`
- `RepairResponse`: `{ fixed: bool, normalizedData: dict | null, changes: list[str], error: str | null }`
- `GenerateCodeRequest`: `{ chartType: str, data: Any, theme: str | "default" }`
- `GenerateCodeResponse`: `{ code: str, error: str | null }`

Supported `chartType` values: `bar`, `line`, `pie`, `doughnut`, `area`, `scatter`.

### Data Schema

Most chart types expect:

```json
{
  "labels": ["A", "B"],
  "datasets": [{ "label": "Series 1", "data": [1, 2] }]
}
```

`scatter` expects:

```json
{
  "datasets": [{ "label": "S1", "data": [{ "x": 1, "y": 2 }] }]
}
```

`pie` and `doughnut` accept only a single dataset.

---

## Code Organisation

### Backend

- `app/main.py` — FastAPI factory, middleware logging, CORS, exception handler, `/health`.
- `app/api/` — One route module per endpoint. Keep endpoints thin; business logic belongs in `services/`.
- `app/schemas/chart.py` — Single source of truth for request/response shapes and validation models.
- `app/services/`
  - `validator.py` — Pydantic-based validation with chart-type-specific rules.
  - `normalizer.py` — Best-effort structural normalisation (key aliases, flat `data` → `datasets`).
  - `llm_service.py` — Provider-agnostic async client with retries and timeouts; logs every call, retry and outcome.
  - `repair_prompt.py` — Builds the repair system prompt with the correct target schema for the selected chart type.
  - `sandbox.py` — Light regex sanitisation before returning LLM-generated HTML.
- `app/prompts/` — Plain-text prompt templates loaded at import time.
- `tests/` — pytest tests importing `app.services.*`.

### Frontend

- `src/App.tsx` — Root layout and component composition.
- `src/components/` — React components. Prefer functional components.
- `src/hooks/` — Custom hooks, including validation debouncing and ECharts option generation.
- `src/store/useStudioStore.ts` — Global Zustand store; owns async validation/repair flows and logs state changes.
- `src/services/api.ts` — Thin `fetch` wrapper around the backend API.
- `src/types/index.ts` — TypeScript domain types mirroring backend schemas.
- `src/utils/chartConfigBuilders/` — One pure function per chart type returning `EChartsOption`.
- `src/utils/colorPalette.ts` — Theme-aware HSL colour generation.
- `src/utils/schemaValidator.ts` — Client-side pre-check helper.

---

## Development Conventions

### Python

- Target Python 3.12.
- Use type hints where practical.
- Prefer explicit relative imports inside `app/` (e.g. `from ..schemas.chart import ...`).
- Use `logging` with structured key=value messages for observability.
- Keep route handlers thin; put business logic in `services/`.
- Pydantic models live in `schemas/chart.py`.
- Prompts are plain text files under `app/prompts/` and read with `Path(...).read_text(encoding="utf-8")`.

### TypeScript / React

- Target `ES2020`; module system `ESNext` with Vite bundler resolution.
- Strict TypeScript is enabled.
- Use functional components and hooks. Class components are reserved for `ErrorBoundary`.
- Use Zustand selectors to avoid unnecessary re-renders.
- ECharts is imported via tree-shaken sub-packages (`echarts/core`, `echarts/charts`, `echarts/components`, `echarts/renderers`).
- Chart builders are pure functions taking `(data, theme)` and returning `EChartsOption`.
- The API base URL is read from `import.meta.env.VITE_API_BASE_URL`.

### CSS

- Global styles are in `src/styles.css` using CSS custom properties.
- No CSS-in-JS or Tailwind is currently used.

---

## Testing Instructions

### Backend

```bash
cd backend
pytest
```

Tests import directly from `app.services.*`. There is no `pytest.ini` or `conftest.py`; the working directory must be `backend/` so module imports resolve.

Current test files:

- `tests/test_validator.py`
- `tests/test_normalizer.py`
- `tests/test_llm_service.py` (only checks static config values)

### Frontend

```bash
cd frontend
npm test
```

This runs Vitest. There are currently no test files under `src/`.

### Manual End-to-End Verification

1. Start the backend.
2. Start the frontend.
3. Paste valid chart JSON into the editor and confirm the status becomes **Valid** and the ECharts preview renders.
4. Introduce a schema error and confirm validation shows actionable errors.
5. Confirm that invalid JSON is NOT automatically repaired. Click the **Ask AI to repair** button and confirm the editor is rewritten with valid JSON and the status becomes **AI repaired the schema**. The button remains available for manual retries.
6. Click **Generate with AI** and confirm a self-contained HTML preview renders in the iframe.

---

## Deployment Notes

- `docker-compose.yml` builds the backend and frontend services; it maps ports `8000` and `5173`.
- Backend container uses `python:3.12-slim` and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Frontend container uses `node:20-alpine` and runs Vite dev mode with `--host 0.0.0.0`.
- The production frontend build is not served by the current Docker setup; it runs the Vite dev server.
- Secrets live only in `.env`, which is excluded by `.gitignore`.

---

## Security Considerations

- LLM-generated HTML is rendered in a sandboxed iframe (`sandbox="allow-scripts"`) and passed through light regex sanitisation in `backend/app/services/sandbox.py`.
- The sanitiser blocks most iframe src attributes (only `cdnjs.cloudflare.com` is allowed), `window.parent`, `window.top`, cookies, storage APIs, `fetch`, and `XMLHttpRequest`.
- The module docstring explicitly states this is **not a full XSS defence** — the iframe sandbox remains the primary control.
- Backend CORS is configured via `CORS_ORIGINS`; keep it as restrictive as possible for the deployment environment.
- API keys are read from environment variables only.
- There is no authentication/authorization layer in the current codebase; do not expose the backend to untrusted networks without adding one.

---

## Common Tasks

### Add a New Supported Chart Type

1. Add the type to `ChartTypeStr` in `backend/app/schemas/chart.py`.
2. Update validation rules in `backend/app/services/validator.py` if needed.
3. Add a builder in `frontend/src/utils/chartConfigBuilders/`.
4. Register the builder in `frontend/src/hooks/useChartConfig.ts`.
5. Add the option to `frontend/src/components/ChartTypeSelector.tsx`.
6. Add backend and frontend tests if applicable.
7. Update `README.md` and this file.

### Change the LLM Provider

The codebase is intentionally single-provider (Kimi). To switch providers, replace the implementation in `backend/app/services/llm_service.py` and update the environment variables in `.env.example` and `docker-compose.yml`.

### Change the Prompts

- `backend/app/prompts/generate_chart_code.txt` — plain text template for full HTML generation.
- `backend/app/prompts/repair_schema.txt` — template for JSON repair. It uses placeholders `{{CHART_TYPE}}`, `{{TARGET_SCHEMA}}` and `{{EXTRA_RULES}}` which are filled by `backend/app/services/repair_prompt.py`.

Keep prompts concise; the repair endpoint expects raw JSON optionally followed by `CHANGES:` on its own line, and the generate-code endpoint expects a complete HTML document.
