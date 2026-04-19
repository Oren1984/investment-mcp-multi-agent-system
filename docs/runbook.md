# Runbook — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Audience:** Developer / operator running or debugging this system

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker Desktop | ≥ 24 | Docker Compose v2 required (`docker compose`, not `docker-compose`) |
| Python | 3.11+ | Only needed for bare-metal / notebook usage |
| Anthropic API key | Any | Required for live analysis; optional with demo mode |

---

## Quick Start (Docker Compose)

### 1. Clone and configure

```bash
git clone <repo-url>
cd investment-mcp-multi-agent-system

cp .env.example .env
```

Edit `.env`:

```dotenv
# Required: replace with your real key, or leave as-is for demo mode
ANTHROPIC_API_KEY=sk-ant-your-key-here

# true  = no LLM calls, synthetic demo reports (safe without a real key)
# false = live AI analysis (requires valid ANTHROPIC_API_KEY)
DEMO_MODE=true

# Change from defaults only if you have port conflicts
# POSTGRES_PASSWORD=your_secure_password_here
```

### 2. Start all services

```bash
docker compose up -d
```

### 3. Verify all containers are healthy

```bash
docker ps
```

Expected output (all `healthy` or `running`):

```
investment_postgres    pgvector/pgvector:pg16   Up (healthy)
investment_backend     ...                      Up (healthy)
investment_ui          ...                      Up (healthy)
investment_prometheus  ...                      Up
investment_grafana     ...                      Up
```

### 4. Verify backend API

```bash
curl http://localhost:8010/api/v1/health
# {"status":"ok","version":"1.0.0"}

curl http://localhost:8010/api/v1/ready
# {"status":"ok","db":true,"mcp_tools":["stock_price","financial_statements",...]}
```

### 5. Access services

| Service | URL | Notes |
|---------|-----|-------|
| Backend API | http://localhost:8010/api/v1 | REST API |
| API docs (Swagger) | http://localhost:8010/docs | Interactive API explorer |
| Streamlit UI | http://localhost:8501 | Web frontend |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboards (admin/admin by default) |

---

## Environment Variables Reference

All variables are loaded from `.env`. The file is never committed to version control.

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `APP_ENV` | `development` | No | `development` or `production` |
| `DEBUG` | `true` | No | Enable debug mode |
| `LOG_LEVEL` | `INFO` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `json` | No | `json` or `text` |
| `API_KEY` | *(empty)* | No | X-API-Key header value; empty disables auth |
| `RATE_LIMIT_ANALYZE` | `10/minute` | No | SlowAPI format: `N/second`, `N/minute`, `N/hour` |
| `USE_ALEMBIC` | `false` | No | `true` to use Alembic migrations; `false` uses SQLAlchemy `create_all` |
| `POSTGRES_DB` | `investment_db` | Yes | Database name |
| `POSTGRES_USER` | `invest_user` | Yes | Database user |
| `POSTGRES_PASSWORD` | *(set in .env)* | Yes | Database password |
| `DATABASE_URL` | `postgresql://...` | Yes | Sync SQLAlchemy URL |
| `DATABASE_URL_ASYNC` | `postgresql+asyncpg://...` | Yes | Async SQLAlchemy URL |
| `ANTHROPIC_API_KEY` | `sk-ant-your-key-here` | For live mode | API key from console.anthropic.com |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | No | Model ID for agent LLM calls |
| `DEMO_MODE` | `true` | No | `true` forces demo mode regardless of API key |
| `NEWS_API_KEY` | *(empty)* | No | newsapi.org key; fallback sentiment used if absent |
| `ALPHA_VANTAGE_KEY` | *(empty)* | No | Not used by current code; reserved |
| `DEFAULT_ANALYSIS_PERIOD` | `1y` | No | Default period when none specified |
| `MAX_CONCURRENT_RUNS` | `5` | No | ThreadPoolExecutor max workers |
| `CREW_VERBOSE` | `false` | No | Enable verbose CrewAI logging |
| `GRAFANA_USER` | `admin` | No | Grafana login username |
| `GRAFANA_PASSWORD` | *(set in .env)* | No | Grafana login password |
| `BACKEND_URL` | `http://localhost:8000` | No | Used by UI container (internal Docker network) |

---

## Enabling Live AI Analysis

To run real AI-powered analysis (not demo mode):

1. Get an Anthropic API key at https://console.anthropic.com/ → API Keys.

2. Update `.env`:
   ```dotenv
   ANTHROPIC_API_KEY=sk-ant-api-YOUR_REAL_KEY_HERE
   DEMO_MODE=false
   ```

3. Rebuild and restart the backend:
   ```bash
   docker compose build backend
   docker compose up -d backend
   ```

4. Verify the startup log does **not** show the placeholder warning:
   ```bash
   docker logs investment_backend 2>&1 | grep -i "demo\|placeholder\|warn"
   # Should be empty or only show "Application startup complete"
   ```

5. Submit a real analysis:
   ```bash
   curl -X POST http://localhost:8010/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"ticker":"AAPL","period":"1y"}'
   ```
   
   Live analysis takes 60–120 seconds to complete (5 agents × LLM calls).

---

## Stopping and Restarting

```bash
# Stop all containers (data persists)
docker compose down

# Stop and remove all data (clean slate)
docker compose down -v

# Restart only the backend (after code changes)
docker compose build backend
docker compose up -d backend

# Restart a specific service
docker compose restart <service-name>
```

---

## Service Dependencies

```
postgres
  └── backend (waits for postgres healthy)
        └── ui (waits for backend healthy)
prometheus
grafana
```

If backend fails to start, check postgres first:
```bash
docker logs investment_postgres
```

---

## Running Without Docker (Development)

### 1. Start only the database

```bash
docker compose up -d postgres
```

### 2. Install backend dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Export environment variables

```bash
export $(grep -v '^#' ../.env | xargs)
# Override for local (not Docker) postgres
export DATABASE_URL_ASYNC=postgresql+asyncpg://invest_user:your_secure_password_here@localhost:5432/investment_db
export DATABASE_URL=postgresql://invest_user:your_secure_password_here@localhost:5432/investment_db
```

### 4. Run the API server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API is available at http://localhost:8000.

---

## Running Notebooks

Notebooks connect to the backend on port **8010** (Docker Compose host port).

```bash
# Ensure Docker stack is running
docker compose up -d

# Start Jupyter
cd notebooks
pip install jupyter requests matplotlib
jupyter notebook
```

Open notebooks in order:
- `01_demo_walkthrough.ipynb` — Submit and retrieve an analysis run
- `02_technical_architecture.ipynb` — System documentation (markdown only, no backend required)
- `03_demo_scenarios.ipynb` — Multiple ticker scenarios

---

## Common Issues and Fixes

### Backend container exits immediately

```bash
docker logs investment_backend
```

- **"No module named 'crewai'"** → run `docker compose build backend` to reinstall dependencies.
- **"could not connect to server"** → postgres not yet healthy; wait 10–15 seconds and retry.

### POST /api/v1/analyze returns 422

- Ensure `Content-Type: application/json` header is set.
- Ticker must be 1–10 characters. Period must be one of: `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`.

### Analysis runs stuck in PENDING

```bash
docker logs investment_backend | grep -i "error\|exception"
```

- If placeholder API key is shown: set `DEMO_MODE=true` or provide a real `ANTHROPIC_API_KEY`.
- If ThreadPoolExecutor is exhausted: wait for current runs to complete or reduce `MAX_CONCURRENT_RUNS`.

### Analysis run status is FAILED

```bash
curl http://localhost:8010/api/v1/analyze/<run_id>/status | jq '.error_message'
```

Common messages:
- `"Anthropic API authentication failed (401)"` → invalid or missing `ANTHROPIC_API_KEY`
- yfinance error → invalid ticker symbol or network issue fetching market data

### GET /api/v1/analyze returns 500

Run was triggered before the `selectinload` fix was applied. Rebuild the backend:
```bash
docker compose build backend && docker compose up -d backend
```

### UI container unhealthy

```bash
docker logs investment_ui
```

The UI Dockerfile healthcheck uses Python's `urllib.request`. If the container shows unhealthy immediately, wait 30 seconds — the startup grace period may not have elapsed.

### Prometheus not scraping

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'
```

Ensure the backend is running and `/metrics` returns data:
```bash
curl http://localhost:8010/metrics | head -5
```

### Database schema issues after code changes

If models change, drop and recreate the database:
```bash
docker compose down -v
docker compose up -d
```

Or use Alembic if migrations are in place:
```bash
# Inside running backend container
docker exec investment_backend alembic upgrade head
```

---

## Logs Reference

```bash
# All services
docker compose logs -f

# Backend only (structured JSON)
docker logs investment_backend 2>&1 | python -m json.tool | head -50

# Filter for errors
docker logs investment_backend 2>&1 | grep '"level":"ERROR"'

# Filter by run_id
docker logs investment_backend 2>&1 | grep '<your-run-id>'
```

---

## Running Tests

```bash
cd backend

# Unit tests only (no database or docker required)
pytest tests/unit/ -v

# Integration tests (requires postgres on localhost:5432)
DATABASE_URL_ASYNC=postgresql+asyncpg://invest_user:your_secure_password_here@localhost:5432/investment_db \
  pytest tests/integration/ -v

# E2E tests (requires full Docker stack running)
pytest tests/e2e/ -v

# Smoke tests
bash ../scripts/smoke_docker.sh
```
