# Testing Matrix — Investment MCP Multi-Agent System

**Date:** 2026-04-23 (Phase 3 hardening pass)
**Total tests:** 210 passing, 0 failing
**Test directories:** `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/e2e/`, `backend/tests/smoke/`

---

## Summary

| Layer | File Count | Test Count | Status |
|-------|-----------|------------|--------|
| Unit | 10 files | 134 | All passing |
| Integration | 5 files | 52 | All passing |
| E2E | 1 file | 5 | All passing |
| Smoke | 2 files | 19 | All passing |
| **Total** | **18 files** | **210** | **All passing** |

---

## Unit Tests

| File | Count | What Is Covered |
|------|-------|-----------------|
| `test_config.py` | 5 | Settings defaults, env var loading, DB URL construction |
| `test_investment_crew.py` | 17 | AnalysisConfig, demo report builder, execution mode routing (demo/rag_only/hybrid/agent_only), error → FAILED status |
| `test_mcp_tools.py` | 16 | MCPRegistry, StockPriceTool, FinancialStatementsTool, RiskMetricsTool, TechnicalIndicatorsTool, NewsSentimentTool, MCPGateway |
| `test_rag_gateway.py` | 19 | execute_rag_pass structure, sources_used/failed, partial failure isolation, _build_rag_snapshot_report (all sections), _format_rag_context_summary |
| `test_rate_limiter.py` | 4 | Rate limit storage, key function |
| `test_report_service.py` | 5 | ReportService.parse_structured, ReportService.save |
| `test_report_validator.py` | 8 | Report section detection, recommendation extraction |
| `test_risk_calculations.py` | 19 | RSI formula edge cases, Sharpe ratio, volatility, max drawdown, RiskService with mocked yfinance |
| `test_schemas.py` | 17 | AnalysisRequest validation, ExecutionMode enum, HealthResponse, ReadyResponse |
| `test_source_registry.py` | 23 | SourceRegistry defaults, record_fetch, update_status, summary, to_dict_list, thread safety, singleton |

---

## Integration Tests

| File | Count | What Is Covered |
|------|-------|-----------------|
| `test_api_analysis.py` | 20 | POST /analyze (submit, validation, mode), GET /analyze/{id}/status, GET /analyze/{id}/report, GET /analyze (history), ExecutionMode field in request/response/status |
| `test_api_auth.py` | 6 | API key auth (no key / correct key / wrong key / missing header), health bypasses auth |
| `test_api_health.py` | 6 | GET /health, GET /ready (tool list), GET /metrics (Prometheus), GET /docs |
| `test_api_sources.py` | 9 | GET /sources (structure, fields, yahoo_finance present, valid statuses), GET /sources/status, no auth required |
| `test_db_repositories.py` | 11 | AnalysisRunRepository CRUD + status transitions, ReportRepository get_by_run_id |

---

## E2E Tests

| File | Count | What Is Covered |
|------|-------|-----------------|
| `test_e2e_analysis.py` | 5 | Full submit→poll→report flow (golden path), invalid ticker rejected, multiple tickers tracked independently, history contains submitted runs, report content coherent |

---

## Smoke Tests

| File | Count | What Is Covered |
|------|-------|-----------------|
| `test_alembic_migration.py` | 5 | alembic.ini exists, env.py importable, initial migration exists and importable, has upgrade/downgrade |
| `test_smoke.py` | 14 | All module imports, MCPGateway tool registration (6 tools), config defaults, RunStatus enum |

---

## Coverage by Component

| Component | Test Layer | Status |
|-----------|-----------|--------|
| `AnalysisConfig` | Unit | Covered |
| `InvestmentCrew` execution modes | Unit | Covered |
| `_build_demo_report` | Unit | Covered |
| `_build_rag_snapshot_report` | Unit | Covered |
| `_format_rag_context_summary` | Unit | Covered |
| `MCPGateway.call()` | Unit | Covered |
| `MCPGateway.execute_rag_pass()` | Unit | Covered |
| `MCPRegistry` | Unit | Covered |
| `StockPriceTool` | Unit | Covered |
| `FinancialStatementsTool` | Unit | Covered |
| `TechnicalIndicatorsTool` | Unit | Covered |
| `RiskMetricsTool` | Unit | Covered |
| `NewsSentimentTool` | Unit | Covered |
| `RiskService` (RSI/Sharpe/Vol/Drawdown) | Unit | Covered |
| `SourceRegistry` | Unit | Covered |
| `ReportService` | Unit | Covered |
| `ReportValidator` | Unit | Covered |
| `AnalysisRequest` / `ExecutionMode` schema | Unit | Covered |
| POST /analyze | Integration | Covered |
| GET /analyze/{id}/status | Integration | Covered |
| GET /analyze/{id}/report | Integration | Covered |
| GET /analyze (history) | Integration | Covered |
| GET /sources | Integration | Covered |
| GET /sources/status | Integration | Covered |
| GET /health | Integration + Smoke | Covered |
| GET /ready | Integration + Smoke | Covered |
| GET /metrics | Integration | Covered |
| API key auth | Integration | Covered |
| DB AnalysisRunRepository | Integration | Covered |
| DB ReportRepository | Integration | Covered |
| Alembic migrations | Smoke | Covered |
| Full E2E flow | E2E | Covered |

---

## What Is Not Covered by Tests

| Area | Reason |
|------|--------|
| Live LLM calls (real Anthropic API) | Requires API key; not run in automated suite |
| Real yfinance market data calls | Mocked in all tests; real data is non-deterministic |
| Docker Compose runtime | Integration-level; requires Docker daemon |
| Kubernetes manifests | Infrastructure; requires cluster |
| Streamlit UI behavior | No browser automation framework added (intentional — adds noise) |
| News API live calls | Mocked; key not configured in test env |
| Load and performance | No stress testing in scope for this phase |
