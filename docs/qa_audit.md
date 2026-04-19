# QA Audit — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Auditor:** Engineering / QA Lead  
**Status:** All critical issues resolved. System operational.

---

## Audit Scope

This audit covered the full backend stack and supporting infrastructure from initial bootstrap through production-readiness testing. The scope included:

- Backend API correctness and error handling
- Dependency configuration
- Database session and ORM usage
- CrewAI agent orchestration
- LLM integration and fallback behavior
- Docker infrastructure and container health
- Jupyter notebook reproducibility
- UI submission flow
- Logging, monitoring, and observability

---

## Components Reviewed

| Component | Location | Reviewed |
|-----------|----------|---------|
| API routes | `backend/app/api/routes/` | ✅ |
| Request schemas | `backend/app/schemas/` | ✅ |
| CrewAI agents | `backend/app/agents/` | ✅ |
| CrewAI tasks | `backend/app/crews/tasks.py` | ✅ |
| Investment crew orchestration | `backend/app/crews/investment_crew.py` | ✅ |
| MCP gateway and tools | `backend/app/mcp/` | ✅ |
| Database models | `backend/app/db/models/` | ✅ |
| Repositories (sync + async) | `backend/app/db/repositories/` | ✅ |
| Services (market, financials, risk, news, LLM, report) | `backend/app/services/` | ✅ |
| Core config and error handling | `backend/app/core/` | ✅ |
| Docker Compose | `docker-compose.yml` | ✅ |
| Dockerfiles | `infra/docker/` | ✅ |
| Environment configuration | `.env`, `.env.example` | ✅ |
| Notebooks | `notebooks/` | ✅ |

---

## Issues Discovered and Fixes Applied

---

### Issue 1 — Backend Startup Failure (Critical)

**Symptom:** `ModuleNotFoundError: No module named 'crewai.tools.base_tool'` on container start.

**Root Cause:** `backend/requirements.txt` specified `crewai>=0.36,<0.50`. No versions in the range 0.36–0.50 exist for Python 3.11. pip resolved to 0.41.1, which does not have the `crewai.tools.base_tool` module. The codebase was written against crewai 1.x (`from crewai import LLM`, `from crewai.tools.base_tool import BaseTool`).

**Fix:** Changed `crewai>=0.36,<0.50` → `crewai>=1.0,<2.0`. Removed `langchain-anthropic>=0.1,<0.4` (unused, conflicted with crewai 1.x). Updated `crewai-tools>=0.4,<0.20` → `crewai-tools>=0.35,<2.0`.

**File:** `backend/requirements.txt`

---

### Issue 2 — HTTP 422 on POST /api/v1/analyze (Critical)

**Symptom:** Every `POST /api/v1/analyze` returned 422 with: `"Field required"` for `body` and `background_tasks` query parameters.

**Root Cause:** `from __future__ import annotations` (line 1 of `analysis.py`) makes all type annotations lazy strings at module load. slowapi's `@limiter.limit()` wraps the route function, and the wrapper's `__globals__` points to `slowapi.extension`, not `app.api.routes.analysis`. FastAPI's `get_typed_signature()` calls `evaluate_forwardref()` using `call.__globals__`. Since `AnalysisRequest` and `BackgroundTasks` are not in slowapi's globals, the `ForwardRef` objects remain unresolved. FastAPI treats unresolved ForwardRefs as required query parameters.

**Confirmed via:** Container inspection showing `body_params: []` and `query_params: [('body', ForwardRef('AnalysisRequest')), ...]`.

**Fix:** Removed `from __future__ import annotations` from `backend/app/api/routes/analysis.py`.

**File:** `backend/app/api/routes/analysis.py`

---

### Issue 3 — GET /api/v1/analyze Returns 500 (High)

**Symptom:** `GET /api/v1/analyze` returned `{"detail":"Unexpected internal error"}`.

**Root Cause:** The list comprehension in `list_history()` accessed `r.report is not None` on each `AnalysisRun` ORM object. The `report` relationship has no eager loading configured. SQLAlchemy 2.0 async sessions do not support implicit lazy loading — accessing the attribute triggers synchronous IO in an async context, raising a `MissingGreenlet` exception.

**Fix:**
1. Added `selectinload` to the import in `analysis_run_repo.py`.
2. Added `.options(selectinload(AnalysisRun.report))` to the `list_recent()` query so the `report` relationship is eagerly fetched in a single JOIN query alongside the run records.

**File:** `backend/app/db/repositories/analysis_run_repo.py`

---

### Issue 4 — UI Container Always Unhealthy (Medium)

**Symptom:** `docker ps` showed UI container with `(unhealthy)` status despite Streamlit running correctly.

**Root Cause:** The Dockerfile healthcheck used `curl --fail http://localhost:8501/_stcore/health`. `curl` is not installed in `python:3.11-slim`.

**Fix:** Replaced the healthcheck command with a pure-Python equivalent using `urllib.request`.

**File:** `infra/docker/ui.Dockerfile`

---

### Issue 5 — Anthropic 401 Authentication Failure (High)

**Symptom:** Analysis runs entered `FAILED` state with `authentication_error: invalid x-api-key`.

**Root Cause:** `.env` contained the template placeholder `ANTHROPIC_API_KEY=sk-ant-your-key-here`. The Docker backend received this value; CrewAI passed it to LiteLLM, which passed it to Anthropic, which returned 401.

**Fix:** Implemented a two-layer response:
1. **Placeholder key detection** — `is_placeholder_key()` in `llm_service.py` detects placeholder, empty, or template keys.
2. **Auto demo mode** — `is_demo_mode()` returns `True` if key is missing/placeholder OR if `DEMO_MODE=true` is set. The crew routes to `_run_demo()` which returns a synthetic, clearly-labelled report without any LLM call.
3. **Startup warning log** — `main.py` logs a `WARNING` on startup if the key is a placeholder.
4. **401 error detection** — The `except` block in `InvestmentCrew.run()` detects "401" / "authentication" / "invalid x-api-key" in the exception message and returns a human-readable error.

**Files:** `backend/app/services/llm_service.py`, `backend/app/crews/investment_crew.py`, `backend/app/main.py`, `.env`

---

### Issue 6 — Notebook 01 NameError on run_id (High)

**Symptom:** Running notebook 01 in order produced `NameError: name 'run_id' is not defined` in the polling cell.

**Root Cause:** The cell that POSTs to `/api/v1/analyze` and captures the returned `run_id` was missing from the notebook. The polling cell referenced `run_id` without it ever being defined.

**Fix:** Inserted a submit cell at index 8 that calls `POST /analyze`, captures `run_id`, and sets `run_id = None` on failure. Added `if run_id is None: skip` guards to the polling and report retrieval cells.

**File:** `notebooks/01_demo_walkthrough.ipynb`

---

### Issue 7 — Notebooks Using Wrong Backend Port (Medium)

**Symptom:** Notebook cells showed `ConnectionRefusedError` when the Docker stack was running.

**Root Cause:** Both notebooks had `BASE_URL = "http://localhost:8000/api/v1"`. Docker Compose maps the backend to host port **8010** (container port 8000).

**Fix:** Changed to `os.getenv("BACKEND_URL", "http://localhost:8010") + "/api/v1"` in both notebooks.

**Files:** `notebooks/01_demo_walkthrough.ipynb`, `notebooks/03_demo_scenarios.ipynb`

---

### Issue 8 — Notebook 03 ConnectionError Blocking All Cells (Medium)

**Symptom:** If the backend was not running, the setup cell crashed with `ConnectionError`, preventing visualization cells that are backend-independent from executing.

**Root Cause:** `requests.get(...).json()["status"]` was called unconditionally in the setup cell.

**Fix:** Wrapped the backend status check in `try/except` with a graceful fallback message. Added a prerequisites markdown cell to document which cells require a live backend vs which run standalone.

**File:** `notebooks/03_demo_scenarios.ipynb`

---

## Post-Fix Validation Summary

| Endpoint / Flow | Before Fixes | After Fixes |
|-----------------|-------------|------------|
| Backend startup | FAIL (import error) | ✅ Clean startup |
| POST /api/v1/analyze | 422 Unprocessable Entity | ✅ 202 Accepted |
| GET /api/v1/analyze/{id}/status | ✅ OK (unaffected) | ✅ OK |
| GET /api/v1/analyze/{id}/report | ✅ OK (unaffected) | ✅ OK |
| GET /api/v1/analyze | 500 Internal Error | ✅ 200 with history |
| GET /api/v1/health | ✅ OK (unaffected) | ✅ OK |
| GET /api/v1/ready | ✅ OK (unaffected) | ✅ OK |
| UI container health | unhealthy | ✅ healthy |
| Demo mode (no API key) | FAILED run | ✅ COMPLETED with demo report |
| Notebook 01 (in order) | NameError | ✅ Runs through |
| Notebook 03 (backend down) | ConnectionError crash | ✅ Graceful fallback |

---

## Remaining Concerns

1. **Sync session management in crew** — `InvestmentCrew.run()` calls `get_sync_session()` directly rather than receiving it as a dependency. This works correctly but limits testability; the session is created per-run and closed in `finally`. No connection leaks observed in testing.

2. **pgvector installed but unused** — The `pgvector` extension is created in `init_db.py` and appears in the Postgres image tag, but no vector columns or similarity searches are implemented. This is dead weight until a feature uses it.

3. **Alpha Vantage and News API keys are optional stubs** — Both keys are read from config but only `news_api_key` has a fallback path (`_fallback_response`). If `alpha_vantage_key` is set, there is no code that uses it. No data quality degradation results, but the config is misleading.

4. **Rate limiter is in-memory only** — SlowAPI uses in-memory state. Running multiple backend replicas would allow each instance its own counter, bypassing the per-IP limit. Acceptable for single-instance deployment; requires Redis for horizontal scaling.

5. **Report section validation is header-text matching only** — `report_validator.py` checks that 6 section headers exist in the report markdown using case-insensitive substring search. It does not validate that sections contain substantive content. A report with six empty section headers would pass validation.
