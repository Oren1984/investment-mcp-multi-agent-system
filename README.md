# Investment MCP Multi-Agent System

A production-grade multi-agent AI system for equity research automation. Five specialized CrewAI agents collaborate via a structured MCP tool gateway to produce multi-section investment analysis reports from a single stock ticker.

---

## Overview

| Layer | Technology |
|-------|-----------|
| Orchestration | CrewAI (sequential process, 5 agents) |
| API | FastAPI (async, Pydantic v2, rate limiting) |
| LLM | Anthropic Claude (claude-sonnet-4-6) |
| Data | yfinance + NewsAPI |
| Tool Protocol | MCP Gateway (6 tools, Pydantic-validated) |
| UI | Streamlit (4 pages) |
| Database | PostgreSQL 16 + pgvector (Alembic migrations) |
| Monitoring | Prometheus + Grafana |
| Infra | Docker Compose + Kubernetes + Terraform (GCP) |

---

## Agents

| Agent | Responsibility | MCP Tools |
|-------|---------------|-----------|
| Research Agent | Market data, fundamentals, news | `get_stock_price`, `get_financial_statements`, `get_news_sentiment` |
| Technical Analyst | Price indicators, trend signals | `get_stock_price`, `get_technical_indicators` |
| Sector Analyst | Industry positioning, ETF comparison | `get_sector_analysis` |
| Risk Analyst | Volatility, drawdown, Sharpe, VaR | `get_risk_metrics` |
| Report Writer | Synthesizes all 4 outputs → structured report | `save_report` |

Agents execute **sequentially**. The Report Writer receives all prior task outputs as context before generating the final report.

---

## Execution Modes

| Mode | Behavior |
|------|----------|
| `hybrid` (default) | Pre-fetches all market data via `execute_rag_pass()`, then runs full agent pipeline with data in context |
| `rag_only` | Fetches data only — no LLM call. Returns a structured snapshot report instantly |
| `agent_only` | Full CrewAI pipeline — agents call MCP tools on demand |

---

## MCP Tool Gateway

The gateway decouples agent logic from service implementations. Every tool call is validated through a Pydantic input schema before execution:

```
get_stock_price       → MarketDataService (yfinance)
get_financial_statements → FinancialsService (yfinance)
get_technical_indicators → RiskService (RSI, MACD, Bollinger, SMA/EMA)
get_risk_metrics      → RiskService (Beta, Sharpe, VaR 95%, drawdown)
get_news_sentiment    → NewsService (NewsAPI / keyword fallback)
get_sector_analysis   → MarketDataService (sector ETF comparison)
save_report           → ReportService (validates sections, persists to DB)
```

`execute_rag_pass()` calls all 6 data tools in one pass with per-tool failure isolation — one failing tool does not abort the full pre-fetch.

---

## Quick Start

```bash
cp .env.example .env
# Required: ANTHROPIC_API_KEY
# Optional: API_KEY (defaults to open), NEWS_API_KEY

docker-compose up --build
```

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze` | POST | Submit analysis (`ticker`, `period`, `execution_mode`) |
| `/api/v1/analyze/{id}/status` | GET | Poll run status |
| `/api/v1/analyze/{id}/report` | GET | Retrieve completed report |
| `/api/v1/analyze` | GET | Analysis history |
| `/api/v1/sources` | GET | Data provider status (SourceRegistry) |
| `/api/v1/sources/status` | GET | Aggregated source health summary |
| `/api/v1/health` | GET | Health check (no auth required) |
| `/api/v1/ready` | GET | Readiness — confirms tool registration |
| `/api/v1/metrics` | GET | Prometheus metrics |

Authentication: `X-API-Key` header (when `API_KEY` env var is set).  
Rate limit: 10 requests/min per IP on POST `/analyze`.

---

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest
```

| Layer | Files | Tests |
|-------|-------|-------|
| Unit | 10 | 134 |
| Integration | 5 | 52 |
| E2E | 1 | 5 |
| Smoke | 2 | 19 |
| **Total** | **18** | **210** |

Test isolation: in-memory SQLite (StaticPool) + FastAPI `dependency_overrides` for DB and gateway. No external network calls in the test suite.

---

## Project Structure

```
investment-mcp-multi-agent-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI route handlers
│   │   ├── crews/          # InvestmentCrew, tasks, execution modes
│   │   ├── mcp/            # MCPGateway, MCPRegistry, 6 tool classes
│   │   ├── services/       # MarketData, Financials, Risk, News, LLM, Report
│   │   ├── db/             # Models, repositories, Alembic migrations
│   │   └── schemas/        # Pydantic request/response models
│   └── tests/              # unit/ integration/ e2e/ smoke/
├── ui/app/                 # Streamlit pages (Analyze, Results, History, Sources)
├── infra/                  # Docker, Kubernetes, Terraform
├── monitoring/             # Prometheus config, Grafana dashboards
├── notebooks/              # Demo walkthrough, architecture, scenarios
├── docs/                   # API contracts, runbook, QA audit, testing matrix
├── static-site/            # Portfolio landing page
└── docker-compose.yml
```

---

## Observability

- **Prometheus** scrapes `/metrics` every 15s — request counts, latency histograms, Python process metrics
- **Grafana** dashboard auto-provisioned from `monitoring/grafana/dashboards/overview.json`
- **Structured logging** — JSON log lines carry `run_id` via `ContextVar` propagated through `copy_context()` into executor threads

---

## Known Limitations

- In-process `SourceRegistry` and rate limiter are not shared across replicas — multi-pod deployments need Redis-backed alternatives
- No RBAC — single API key; no per-user audit trail
- yfinance data reliability for small-cap, OTC, or very recent IPOs is variable
- LLM calls are not tested in the automated suite (requires live Anthropic API key)

---

## Documentation

| File | Contents |
|------|----------|
| `docs/api_contracts.md` | Full endpoint contracts with request/response schemas |
| `docs/runbook.md` | Deployment, configuration, troubleshooting |
| `docs/testing_matrix.md` | Complete test inventory (210 tests, per-component coverage) |
| `docs/qa_audit.md` | Phase 3 QA audit — 5 bugs found and fixed |
| `docs/known_limitations.md` | Detailed limitations and mitigation notes |

---

## Demo Assets

| Asset | Purpose |
|-------|---------|
| `notebooks/01_demo_walkthrough.ipynb` | End-to-end user flow walkthrough |
| `notebooks/02_technical_architecture.ipynb` | Engineering deep dive for technical reviewers |
| `notebooks/03_demo_scenarios.ipynb` | Stock scenarios + risk metric interpretation guide |
| `static-site/index.html` | Portfolio landing page with interactive demo |

---

## Author

Oren Salami — AI Systems Engineer
