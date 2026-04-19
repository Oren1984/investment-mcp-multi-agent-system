# Testing Matrix — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Test directories:** `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/e2e/`, `backend/tests/smoke/`

---

## Coverage Summary

| Layer | Files Present | Estimated Coverage | Status |
|-------|-------------|-------------------|--------|
| Unit tests | Yes | Core components covered | Partial |
| Integration tests | Yes | API + DB paths | Partial |
| E2E tests | Yes | Submit → poll → report | Partial |
| Smoke tests | Yes | Docker stack + Alembic | Present |

> **Note:** Test files exist and are structured but the test suite has not been run in CI. Coverage percentages are estimated from file presence and content inspection, not from a coverage report tool.

---

## Unit Tests

| Component | Test File | What Is Tested | Status |
|-----------|-----------|----------------|--------|
| Settings / Config | `unit/test_config.py` | Env var loading, demo_mode flag, API key presence | ✅ Present |
| MCP Tool: StockPrice | `unit/test_mcp_tools.py` | Tool input validation, result structure | ✅ Present |
| MCP Tool: FinancialStatements | `unit/test_mcp_tools.py` | Statement type routing, key metrics structure | ✅ Present |
| MCP Tool: TechnicalIndicators | `unit/test_mcp_tools.py` | Indicator presence in output dict | ✅ Present |
| MCP Tool: SectorAnalysis | `unit/test_mcp_tools.py` | Sector ETF comparison structure | ✅ Present |
| MCP Tool: RiskMetrics | `unit/test_mcp_tools.py` | Beta, VaR, Sharpe presence | ✅ Present |
| MCP Tool: NewsSentiment | `unit/test_mcp_tools.py` | Sentiment label, headline list | ✅ Present |
| MCP Tool: SaveReport | `unit/test_mcp_tools.py` | Section validation, DB persistence mock | ✅ Present |
| Rate limiting | `unit/test_rate_limiting.py` | 429 after threshold, header presence | ✅ Present |
| ReportService | `unit/test_report_service.py` | `parse_structured()` section extraction, `save()` | ✅ Present |
| Report validator | `unit/test_report_validator.py` | 6-section check, missing section detection | ✅ Present |
| Risk calculations | `unit/test_risk_calculations.py` | Beta, VaR, Sharpe formulas | ✅ Present |
| Schemas | `unit/test_schemas.py` | Pydantic validation for request/response types | ✅ Present |
| LLMService | Not found | `is_placeholder_key()`, `is_demo_mode()` | ❌ Not present |
| MCPRegistry | Not found | `register()`, `get()`, ToolNotFoundError | ❌ Not present |

---

## Integration Tests

| Component | Test File | What Is Tested | Status |
|-----------|-----------|----------------|--------|
| POST /api/v1/analyze | `integration/test_api_analysis.py` | 202 response, run_id in body, DB row created | ✅ Present |
| GET /api/v1/analyze/{id}/status | `integration/test_api_analysis.py` | Status transitions, 404 for unknown id | ✅ Present |
| GET /api/v1/analyze/{id}/report | `integration/test_api_analysis.py` | 202 before complete, 200 after, 404 for unknown | ✅ Present |
| GET /api/v1/analyze (history) | `integration/test_api_analysis.py` | Items returned, has_report flag | ✅ Present |
| Auth: X-API-Key header | `integration/test_auth.py` | 401 when key set but missing, 200 when correct | ✅ Present |
| Auth: disabled (no API_KEY) | `integration/test_auth.py` | 200 without header when API_KEY empty | ✅ Present |
| GET /api/v1/health | `integration/test_health.py` | `{"status":"ok"}`, HTTP 200 | ✅ Present |
| GET /api/v1/ready | `integration/test_health.py` | db=true when DB connected, mcp_tools list populated | ✅ Present |
| AnalysisRunRepository (async) | `integration/test_db_repositories.py` | create(), get(), list_recent(), update_status() | ✅ Present |
| ReportRepository (async) | `integration/test_db_repositories.py` | get_by_run_id(), list_by_ticker() | ✅ Present |
| Async session + selectinload | Not confirmed separate | Eager load of report in list_recent() | ⚠️ Covered indirectly |

---

## End-to-End Tests

| Scenario | Test File | What Is Tested | Status |
|----------|-----------|----------------|--------|
| Full demo mode pipeline | `e2e/test_e2e_analysis.py` | Submit → poll → complete → report | ✅ Present |
| Run with invalid ticker (live) | `e2e/test_e2e_analysis.py` | FAILED status, error_message set | ⚠️ Requires live mode |
| Concurrent runs | Not confirmed | Race conditions, separate run_ids | ❌ Not confirmed |

---

## Smoke Tests

| Test | File | What Is Tested | Status |
|------|------|----------------|--------|
| Alembic migration | `smoke/test_alembic.py` | `alembic upgrade head` runs cleanly | ✅ Present |
| Docker stack smoke | `scripts/smoke_docker.sh` | All containers healthy, health endpoint responds | ✅ Present |

---

## Component-Level Coverage Matrix

| Component | Unit | Integration | E2E | Smoke | Overall |
|-----------|------|-------------|-----|-------|---------|
| `api/routes/analysis.py` | — | ✅ | ✅ | ✅ | Good |
| `api/routes/health.py` | — | ✅ | — | ✅ | Good |
| `api/deps.py` (auth) | — | ✅ | — | — | Partial |
| `api/limiter.py` | ✅ | — | — | — | Partial |
| `core/config.py` | ✅ | — | — | — | Partial |
| `core/errors.py` | — | ⚠️ | — | — | Low |
| `db/models/*` | — | ✅ | ✅ | — | Good |
| `db/repositories/analysis_run_repo.py` | — | ✅ | ✅ | — | Good |
| `db/repositories/report_repo.py` | — | ✅ | ✅ | — | Good |
| `db/session.py` | — | ✅ | — | — | Partial |
| `services/llm_service.py` | ❌ | — | — | — | None |
| `services/market_data_service.py` | — | — | — | — | None |
| `services/financials_service.py` | — | — | — | — | None |
| `services/risk_service.py` | ✅ | — | — | — | Partial |
| `services/news_service.py` | — | — | — | — | None |
| `services/report_service.py` | ✅ | ✅ | ✅ | — | Good |
| `mcp/gateway.py` | — | — | — | — | None |
| `mcp/registry.py` | — | — | — | — | None |
| `mcp/tools/*` | ✅ | — | — | — | Partial |
| `agents/*` | — | — | — | — | None |
| `crews/investment_crew.py` | — | — | ✅ | — | Partial |
| `crews/tasks.py` | — | — | — | — | None |
| `utils/report_validator.py` | ✅ | — | — | — | Partial |
| `api/middleware.py` | — | — | — | — | None |

---

## Coverage Gaps

The following components have no test coverage and represent risk:

| Component | Risk Level | Notes |
|-----------|------------|-------|
| `services/llm_service.py` | High | `is_placeholder_key()` and `is_demo_mode()` are critical branches |
| `services/market_data_service.py` | Medium | yfinance calls will fail on network isolation |
| `services/news_service.py` | Medium | Fallback path logic not exercised |
| `mcp/gateway.py` | Medium | Singleton initialization, tool dispatch |
| `agents/*` (all 5) | Low-Medium | Agent configs — hard to unit test; covered by E2E |
| `crews/tasks.py` | Low | Task prompts — change detection only |
| `api/middleware.py` | Low | Correlation ID propagation |

---

## How to Run Tests

```bash
# From repository root
docker compose up -d postgres

cd backend

# Unit tests only (no DB)
pytest tests/unit/ -v

# Integration tests (requires running postgres)
DATABASE_URL_ASYNC=postgresql+asyncpg://invest_user:your_secure_password_here@localhost:5432/investment_db \
  pytest tests/integration/ -v

# E2E tests (requires full Docker stack)
docker compose up -d
pytest tests/e2e/ -v

# Smoke tests
bash scripts/smoke_docker.sh
```
