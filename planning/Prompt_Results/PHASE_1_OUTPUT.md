# Phase 1 Output — Audit, Cleanup & Rebuild Plan
## Investment MCP Multi-Agent System

**Date:** 2026-04-19  
**Status:** COMPLETE — Awaiting approval before Phase 2

---

## 🔍 Repository Audit

### What Exists

| Component | Type | Description |
|-----------|------|-------------|
| `shared-platform/` | Template skeleton | Config, logging, errors, base classes, resilience, integrations, LLM gateway, telemetry, security, validation, evaluation, mlops, feature flags, schemas, docker, CI |
| `agent-system-skeleton/` | Template skeleton | FastAPI main, planner/orchestration, BaseTool, provider adapters (Anthropic/OpenAI/Gemini), memory store, web search connector, approval gate, MCP integration notes, agents dir, observability, policies, tests |
| `rag-system-skeleton/` | Template skeleton | Full RAG pipeline dirs (chunking, embeddings, reranking, retrieval, vector_store, grounding, ingestion, prompting), FastAPI API, app structure, providers, security, session, tests, data dirs, infra (docker/terraform), notebooks |
| `streamlit-ui-skeleton/` | Template skeleton | Pages, components, services, utils, assets, config, tests, minimal requirements.txt |
| `planning/` | Planning docs | Phase 1–5 plan templates |

### What Is Useful

| Item | Why Useful |
|------|-----------|
| `shared-platform/config/settings.py` | Solid env-loader with dotenv, reusable as-is |
| `shared-platform/app_logging/` | Structured logging foundation to build on |
| `shared-platform/errors/` | Base error hierarchy for consistent error handling |
| `shared-platform/base/` | `BaseComponent`, `BaseService` — proper ABC contracts |
| `shared-platform/resilience/` | Retry/timeout framework |
| `shared-platform/integrations/llm/` | `BaseLLMClient`, `PromptTemplate` — extend for Anthropic |
| `shared-platform/integrations/external_apis/` | `BaseApiClient` — extend for Yahoo Finance, NewsAPI |
| `shared-platform/integrations/vector_db/` | `BaseVectorClient` — extend for pgvector |
| `shared-platform/telemetry/` | Telemetry conventions to wire into Prometheus |
| `shared-platform/schemas/` | Pydantic schema standards |
| `shared-platform/security_baselines/` | Security conventions |
| `agent-system-skeleton/tools/base_tool.py` | Clean `BaseTool` ABC — use directly |
| `agent-system-skeleton/orchestration/planner.py` | Lightweight plan structures, adapt for CrewAI |
| `agent-system-skeleton/approvals/approval_gate.py` | Human-in-the-loop gate — relevant for high-risk actions |
| `agent-system-skeleton/providers/adapters/` | Anthropic/OpenAI/Gemini adapters — extend as needed |
| `rag-system-skeleton/rag/` | Directory structure for optional pgvector RAG |
| `streamlit-ui-skeleton/app/` | Page/component/service structure — use as-is |
| `agent-system-skeleton/docker-compose.yml` | Basic compose starting point |

### What Is Redundant

| Item | Reason |
|------|--------|
| `rag-system-skeleton/data/` | Empty placeholder dirs, not needed |
| `rag-system-skeleton/examples/` | Empty README only |
| `rag-system-skeleton/session/` | Not relevant to investment system |
| `rag-system-skeleton/connectors/web_search/` | Duplicated from agent-system-skeleton |
| `agent-system-skeleton/connectors/web_search/` | Will be replaced by MCP tools |
| `shared-platform/mlops/experiment_tracking/` | MLOps is DS/ML concern, not agent system |
| `shared-platform/feature_flags/` | Premature for this system |
| `shared-platform/evaluation/benchmarks/` | Empty, not needed yet |
| `agent-system-skeleton/memory/checkpoints/`, `short_term/`, `long_term/` | Empty placeholder dirs; memory will be in PostgreSQL |
| `agent-system-skeleton/notebooks/` | Explicitly excluded in Phase 1 |
| `rag-system-skeleton/notebooks/` | Explicitly excluded in Phase 1 |
| All `README.md` stub files inside skeletons | Replace with domain-specific docs |

### What Must Be Removed

| Item | Action |
|------|--------|
| `rag-system-skeleton/data/raw/`, `data/processed/`, `data/samples/` | Remove — no raw data storage in this project |
| `rag-system-skeleton/examples/` | Remove |
| `agent-system-skeleton/notebooks/` | Remove for Phase 1–2 |
| `rag-system-skeleton/notebooks/` | Remove for Phase 1–2 |
| `shared-platform/mlops/` | Remove — DS/ML concern |
| `shared-platform/feature_flags/` | Remove — premature complexity |
| `shared-platform/evaluation/benchmarks/`, `evaluation/test_cases/` | Remove — out of scope |

### What Is Missing (Must Be Built)

| Missing Layer | Description |
|---------------|-------------|
| `backend/` | Full FastAPI service with proper structure |
| `backend/app/agents/` | CrewAI agent implementations |
| `backend/app/crews/` | CrewAI crew definitions |
| `backend/app/mcp/` | MCP tool gateway and tool registry |
| `backend/app/mcp/tools/` | All investment tools (price, financials, technicals, risk, news) |
| `backend/app/services/` | MarketDataService, NewsService, FinancialsService |
| `backend/app/db/` | SQLAlchemy models, Alembic migrations |
| `infra/docker/` | Production Dockerfiles |
| `infra/k8s/` | K8s manifests |
| `infra/terraform/` | GCP Terraform modules |
| `monitoring/` | Prometheus config + Grafana dashboards |
| `docker-compose.yml` | Full compose (backend, ui, postgres+pgvector, prometheus, grafana) |
| `.env.example` | Consolidated environment variable reference |

---

## 🧼 Cleanup Plan

| Item | Action | Reason |
|------|--------|--------|
| `shared-platform/` | Keep + Extract modules into `backend/app/core/` | Valuable foundation; copy relevant modules |
| `agent-system-skeleton/tools/base_tool.py` | Keep → move to `backend/app/mcp/base_tool.py` | Clean interface for all MCP tools |
| `agent-system-skeleton/orchestration/` | Keep as reference → replace with CrewAI | Structure reference; CrewAI manages actual orchestration |
| `agent-system-skeleton/approvals/approval_gate.py` | Keep → integrate into API flow | Human-in-the-loop before final report generation |
| `agent-system-skeleton/providers/adapters/` | Keep → extend AnthropicAdapter | Claude 3.5 Sonnet will power all agents |
| `agent-system-skeleton/connectors/web_search/` | Remove | Replaced by dedicated MCP tools |
| `agent-system-skeleton/memory/checkpoints/`, `short_term/`, `long_term/` | Remove | Memory is PostgreSQL-backed |
| `agent-system-skeleton/notebooks/` | Remove | Out of scope (Phase 4) |
| `agent-system-skeleton/planning/` | Remove | Replaced by `/planning/` at root |
| `agent-system-skeleton/integrations/mcp/README.md` | Keep as reference | Useful MCP design notes |
| `rag-system-skeleton/rag/` | Keep skeleton structure only | Reference for pgvector RAG (optional) |
| `rag-system-skeleton/data/` | Remove | Empty placeholder, no data storage |
| `rag-system-skeleton/examples/` | Remove | Empty |
| `rag-system-skeleton/session/` | Remove | Irrelevant |
| `rag-system-skeleton/connectors/` | Remove | Duplicate |
| `rag-system-skeleton/notebooks/` | Remove | Out of scope |
| `streamlit-ui-skeleton/` | Keep + Rename to `ui/` | Will be built into the UI layer |
| `shared-platform/mlops/` | Remove | DS/ML concern, not agent system |
| `shared-platform/feature_flags/` | Remove | Premature |
| `shared-platform/evaluation/benchmarks/`, `test_cases/` | Remove | Out of scope |
| `planning/` | Keep | Phase documentation |

---

## 🏗 Final Architecture

### Layer Breakdown

```
┌─────────────────────────────────────────────────────┐
│                    Streamlit UI                      │
│   (ticker input, analysis config, report viewer)    │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────┐
│                FastAPI Backend                       │
│   (routing, auth, job management, response format)  │
└───────────────────────┬─────────────────────────────┘
                        │ Python calls
┌───────────────────────▼─────────────────────────────┐
│             CrewAI Orchestration Layer               │
│   (crew definition, agent coordination, task flow)  │
└──┬──────────────┬─────────────┬────────────┬────────┘
   │              │             │            │
┌──▼──┐    ┌──────▼──┐   ┌─────▼───┐  ┌────▼──────┐ ┌──────────────┐
│ Research│  │Technical│   │  Sector │  │  Risk     │ │   Report     │
│ Agent  │  │ Analyst │   │ Analyst │  │  Analyst  │ │   Writer     │
└──┬──┘    └──────┬──┘   └─────┬───┘  └────┬──────┘ └──────┬───────┘
   └──────────────┴─────────────┴────────────┴──────────────┘
                                │ MCP Tool calls
┌───────────────────────────────▼─────────────────────────────────┐
│                    MCP Tool Gateway                              │
│   (tool registry, input validation, routing, execution)         │
└──┬──────────────┬──────────────┬──────────────┬─────────────────┘
   │              │              │              │
┌──▼────┐  ┌──────▼───┐  ┌──────▼──┐  ┌───────▼────┐
│Market │  │  News    │  │Financial│  │  Risk      │
│ Data  │  │ Service  │  │ Service │  │  Service   │
│Service│  └──────────┘  └─────────┘  └────────────┘
└──┬────┘
   │
┌──▼──────────────────────────────────────────────────────────────┐
│             External APIs (Yahoo Finance, NewsAPI, etc.)        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL (+ pgvector optional)               │
│   analysis_runs | agent_outputs | reports | document_embeddings │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Prometheus + Grafana (Monitoring)                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| **Streamlit UI** | User input (ticker, date range, analysis type), job status display, report rendering, download |
| **FastAPI Backend** | REST API, request validation, job queuing, response serialization, error handling |
| **CrewAI Orchestration** | Define crews, assign tasks to agents, manage sequential/parallel execution, aggregate outputs |
| **Agents** | Domain-specific analysis via tool calls + LLM synthesis |
| **MCP Tool Gateway** | Tool registry, input/output schema validation, tool execution, error propagation |
| **Services** | External API abstraction (market data, news, financials), caching, rate limiting |
| **PostgreSQL** | Persist analysis runs, agent outputs, final reports; optional document embeddings |
| **Monitoring** | Metrics exposition, latency tracking, error rates, Grafana visualization |

### Data Flow

```
1. User enters ticker + analysis config in Streamlit
2. Streamlit POSTs to FastAPI /api/v1/analyze
3. FastAPI validates request, creates analysis_run record in PostgreSQL (status=PENDING)
4. FastAPI invokes CrewAI crew asynchronously (BackgroundTask)
5. CrewAI runs agents in sequence:
   a. ResearchAgent  → calls get_financial_statements, get_stock_price tools
   b. TechAnalystAgent → calls get_technical_indicators tool
   c. SectorAnalystAgent → calls get_sector_analysis tool
   d. RiskAnalystAgent → calls get_risk_metrics tool
   e. ReportWriterAgent → calls save_report tool; synthesizes all agent outputs via LLM
6. Each agent output saved to agent_outputs table
7. Final report saved to reports table; analysis_run status=COMPLETED
8. Streamlit polls GET /api/v1/analyze/{run_id}/status
9. On completion, Streamlit fetches GET /api/v1/analyze/{run_id}/report
10. Report rendered in Streamlit; user can download PDF/JSON
```

### Component Boundaries

- **UI ↔ Backend**: REST/JSON over HTTP. No direct DB access from UI.
- **Backend ↔ CrewAI**: In-process Python call. CrewAI runs as library, not a microservice.
- **Agents ↔ MCP Tools**: Standard MCP tool call interface (`BaseTool.run(payload)`).
- **MCP Tools ↔ Services**: Services are injected into tools. Services own external API calls.
- **Services ↔ External APIs**: Services handle auth, rate limiting, retries.
- **All layers ↔ PostgreSQL**: SQLAlchemy ORM with Alembic migrations. Only backend writes to DB.

---

## 🤖 Agents Plan

### 1. Research Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Collect fundamental data on a given ticker |
| **LLM Role** | Synthesize raw financials into a summary paragraph with key takeaways |
| **Inputs** | ticker symbol, fiscal_year |
| **Outputs** | Fundamental summary: revenue trend, earnings, P/E, P/B, growth rate, balance sheet health |
| **Tools** | `get_financial_statements`, `get_stock_price`, `get_company_overview` |
| **Dependencies** | FinancialsService (Yahoo Finance / Alpha Vantage) |

### 2. Technical Analyst Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Evaluate price action and momentum indicators |
| **LLM Role** | Interpret indicator signals and produce a technical outlook (bullish/bearish/neutral) |
| **Inputs** | ticker symbol, date_range |
| **Outputs** | Technical analysis: trend direction, momentum score, support/resistance levels, indicator summary |
| **Tools** | `get_technical_indicators`, `get_stock_price` |
| **Dependencies** | MarketDataService |

### 3. Sector Analyst Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Contextualize the ticker within its sector and vs. peers |
| **LLM Role** | Compare the company to sector ETF and top peers, identify relative strength/weakness |
| **Inputs** | ticker symbol, sector name |
| **Outputs** | Sector positioning: vs. sector ETF performance, peer comparison table, relative valuation |
| **Tools** | `get_sector_analysis`, `get_stock_price` |
| **Dependencies** | MarketDataService |

### 4. Risk Analyst Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Quantify investment risk profile |
| **LLM Role** | Translate raw risk metrics into an investment risk narrative |
| **Inputs** | ticker symbol, date_range |
| **Outputs** | Risk profile: beta, annualized volatility, max drawdown, Sharpe ratio, VaR (95%) |
| **Tools** | `get_risk_metrics` |
| **Dependencies** | MarketDataService |

### 5. Report Writer Agent

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Synthesize all agent outputs into a structured investment report |
| **LLM Role** | Primary synthesis agent; produces the final document |
| **Inputs** | Outputs from all 4 agents above |
| **Outputs** | Full investment report: executive summary, fundamentals, technicals, sector context, risk, recommendation, disclaimer |
| **Tools** | `save_report` |
| **Dependencies** | All agent outputs, PostgreSQL |

### 6. Macro/News Analyst Agent (Optional Phase 2+)

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Add macro context and recent news sentiment |
| **Inputs** | ticker symbol, company name |
| **Outputs** | News sentiment score, key headlines, macro headwinds/tailwinds |
| **Tools** | `get_news_sentiment` |
| **Dependencies** | NewsService (NewsAPI / Tavily) |

---

## 🛠 MCP & Tools Plan

### Tool Registry Structure

```python
# backend/app/mcp/registry.py
TOOL_REGISTRY: dict[str, BaseTool] = {
    "get_stock_price":          StockPriceTool,
    "get_financial_statements": FinancialStatementsTool,
    "get_technical_indicators": TechnicalIndicatorsTool,
    "get_sector_analysis":      SectorAnalysisTool,
    "get_risk_metrics":         RiskMetricsTool,
    "get_news_sentiment":       NewsSentimentTool,    # optional
    "search_documents":         DocumentSearchTool,   # optional RAG
    "save_report":              SaveReportTool,
}
```

### Tool Definitions

| Tool | Inputs | Outputs | Service Used | Read-Only |
|------|--------|---------|-------------|-----------|
| `get_stock_price` | ticker, start_date, end_date, interval | OHLCV data, current price | MarketDataService | Yes |
| `get_financial_statements` | ticker, statement_type, period | Income/balance/cashflow tables | FinancialsService | Yes |
| `get_technical_indicators` | ticker, indicators[], period | RSI, MACD, SMA, EMA, Bollinger values | MarketDataService | Yes |
| `get_sector_analysis` | ticker, sector | Sector ETF comparison, peer list + prices | MarketDataService | Yes |
| `get_risk_metrics` | ticker, period | beta, volatility, VaR, Sharpe, max_drawdown | MarketDataService | Yes |
| `get_news_sentiment` | ticker, company_name, days | headline list, sentiment scores, avg_sentiment | NewsService | Yes |
| `search_documents` | query, top_k | Document chunks + metadata | EmbeddingService | Yes |
| `save_report` | run_id, report_data | report_id, saved_at | PostgreSQL | No |

### Input Validation Approach

- All tool inputs validated by **Pydantic models** before execution
- Invalid inputs return structured `ToolValidationError` — never raw exceptions to agents
- Each tool defines an `InputSchema(BaseModel)` and `OutputSchema(BaseModel)`

### Routing Logic

- Agents call tools through `MCPToolGateway.call(tool_name, payload)`
- Gateway looks up tool in registry, validates input, executes, validates output
- Errors wrapped in `ToolExecutionResult(success=False, error=...)`
- Agents receive structured result; LLM handles error context in its reasoning

---

## 🗄 Database Plan

### Tables

```sql
-- Ticker metadata cache
CREATE TABLE tickers (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol        VARCHAR(10) UNIQUE NOT NULL,
    company_name  TEXT,
    sector        TEXT,
    industry      TEXT,
    exchange      TEXT,
    last_updated  TIMESTAMP DEFAULT NOW()
);

-- Analysis job tracking
CREATE TABLE analysis_runs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker_id     UUID REFERENCES tickers(id),
    status        VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    config        JSONB,                              -- analysis parameters
    created_at    TIMESTAMP DEFAULT NOW(),
    started_at    TIMESTAMP,
    completed_at  TIMESTAMP,
    error_message TEXT
);

-- Raw outputs from each agent
CREATE TABLE agent_outputs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID REFERENCES analysis_runs(id),
    agent_name    VARCHAR(50) NOT NULL,
    output_data   JSONB NOT NULL,
    tool_calls    JSONB,                              -- audit trail
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Final synthesized reports
CREATE TABLE reports (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID REFERENCES analysis_runs(id) UNIQUE,
    ticker_symbol VARCHAR(10),
    content       TEXT NOT NULL,                     -- markdown report
    structured    JSONB,                             -- parsed sections
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Optional: document embeddings (pgvector)
CREATE TABLE document_embeddings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker_symbol VARCHAR(10),
    doc_type      VARCHAR(50),                       -- 'SEC_10K', 'EARNINGS_CALL', etc.
    chunk_text    TEXT NOT NULL,
    embedding     vector(1536),                      -- OpenAI/Anthropic embedding dim
    metadata      JSONB,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON document_embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Key Relationships

- `analysis_runs` → `tickers` (many-to-one)
- `agent_outputs` → `analysis_runs` (many-to-one)
- `reports` → `analysis_runs` (one-to-one)
- `document_embeddings` → loosely linked via `ticker_symbol`

### Storage Strategy

- All analysis outputs stored as JSONB for flexibility
- Reports stored as both markdown text (human-readable) and structured JSONB (for UI parsing)
- Ticker table acts as a cache to avoid repeated company lookup API calls
- pgvector enabled via `CREATE EXTENSION IF NOT EXISTS vector;` on startup

---

## 🧪 Testing Plan

### Unit Tests

| Scope | Coverage |
|-------|----------|
| MCP tools | Input validation, output schema correctness, error handling |
| Services | Mock external API responses, verify data transformation |
| Pydantic schemas | Edge cases, required fields, type coercion |
| CrewAI agents | Agent config validation, tool assignment |
| DB models | SQLAlchemy model creation, relationships |

**Framework:** `pytest` + `pytest-asyncio` + `pydantic` test utilities

### Integration Tests

| Scope | Coverage |
|-------|----------|
| FastAPI endpoints | Full request/response cycle with test DB |
| MCP Gateway | Tool execution with stubbed services |
| PostgreSQL | Write/read analysis_runs and reports |
| CrewAI crew | End-to-end crew run with mocked LLM and tools |

**Framework:** `pytest` + `httpx` (async client) + `pytest-postgresql` or test container

### Smoke Tests

| Scope | Coverage |
|-------|----------|
| Health checks | `/health`, `/ready` endpoints return 200 |
| DB connectivity | Can write and read one record |
| Tool registry | All tools resolve correctly |
| CrewAI import | Crew can be instantiated without errors |

**Framework:** `pytest` with a `smoke` marker; run after Docker compose up

### E2E Approach (Phase 3)

- Spin up full docker-compose stack
- Submit real ticker via Streamlit session simulation
- Assert report is generated and stored
- Validate report structure and content quality

---

## ⚙️ Infrastructure Plan

### Target Folder Structure

```
infra/
├── docker/
│   ├── backend.Dockerfile
│   └── ui.Dockerfile
├── k8s/
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── ui-deployment.yaml
│   ├── ui-service.yaml
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── modules/
    │   ├── gke/            # Google Kubernetes Engine cluster
    │   ├── cloudsql/       # Cloud SQL (PostgreSQL)
    │   └── artifact_registry/  # Docker image storage
    └── environments/
        ├── dev/
        └── prod/
```

### Docker Structure

| Service | Base Image | Port |
|---------|-----------|------|
| `backend` | `python:3.11-slim` | 8000 |
| `ui` | `python:3.11-slim` | 8501 |
| `postgres` | `pgvector/pgvector:pg16` | 5432 |
| `prometheus` | `prom/prometheus:latest` | 9090 |
| `grafana` | `grafana/grafana:latest` | 3000 |

### docker-compose.yml (Design)

```yaml
services:
  backend:
    build: { context: ./backend, dockerfile: ../infra/docker/backend.Dockerfile }
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres]

  ui:
    build: { context: ./ui, dockerfile: ../infra/docker/ui.Dockerfile }
    ports: ["8501:8501"]
    env_file: .env
    depends_on: [backend]

  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment: { POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD }
    volumes: [postgres_data:/var/lib/postgresql/data]

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes: [./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    volumes: [grafana_data:/var/lib/grafana]
    environment: { GF_SECURITY_ADMIN_PASSWORD }
```

### Kubernetes Resources

| Resource | Type | Purpose |
|----------|------|---------|
| `backend-deployment` | Deployment | FastAPI; 2 replicas min |
| `ui-deployment` | Deployment | Streamlit; 1 replica |
| `postgres-statefulset` | StatefulSet | PostgreSQL with persistent volume |
| `backend-service` | ClusterIP | Internal routing to FastAPI |
| `ui-service` | LoadBalancer / Ingress | External access to UI |
| `configmap` | ConfigMap | Non-secret env vars |
| `secret` | Secret | API keys, DB credentials |

### Terraform (GCP)

| Module | Resource |
|--------|---------|
| `gke` | GKE Autopilot cluster, `us-central1` |
| `cloudsql` | Cloud SQL for PostgreSQL 16 + pgvector |
| `artifact_registry` | Docker image repository |

---

## 📊 Monitoring Plan

### Metrics to Expose (Prometheus)

| Metric | Type | Description |
|--------|------|-------------|
| `analysis_run_total` | Counter | Total analysis runs started |
| `analysis_run_completed_total` | Counter | Total completed runs |
| `analysis_run_failed_total` | Counter | Total failed runs |
| `analysis_run_duration_seconds` | Histogram | End-to-end run time |
| `agent_execution_duration_seconds` | Histogram | Per-agent execution time (label: agent_name) |
| `tool_call_total` | Counter | Tool calls (label: tool_name, status) |
| `tool_call_duration_seconds` | Histogram | Tool execution time (label: tool_name) |
| `external_api_call_total` | Counter | External API calls (label: provider, endpoint) |
| `external_api_latency_seconds` | Histogram | External API latency |
| `http_requests_total` | Counter | FastAPI request count (label: method, path, status) |
| `http_request_duration_seconds` | Histogram | FastAPI request latency |
| `db_query_duration_seconds` | Histogram | PostgreSQL query latency |

### Prometheus Configuration

- FastAPI exposes `/metrics` endpoint via `prometheus-fastapi-instrumentator`
- Prometheus scrapes backend at 15s intervals
- Alert rules: analysis failure rate > 10%, tool latency p99 > 30s, DB connection pool exhaustion

### Grafana Dashboards

| Dashboard | Panels |
|-----------|--------|
| **System Overview** | Analysis runs/min, success rate, p50/p99 latency, active jobs |
| **Agent Performance** | Per-agent execution time, error rate, tool call breakdown |
| **External APIs** | Yahoo Finance/NewsAPI latency, error rates, rate limit proximity |
| **Infrastructure** | CPU/memory usage per service, DB connections, pod health |

### Logging Strategy

- **Format:** Structured JSON logs (via `shared-platform/app_logging/`)
- **Levels:** DEBUG (dev), INFO (prod default), ERROR (always)
- **Key fields:** `run_id`, `agent_name`, `tool_name`, `ticker`, `duration_ms`, `status`
- **Correlation:** `run_id` propagated as log correlation ID across all layers
- **Storage:** stdout → collected by GCP Cloud Logging (prod) or docker logs (local)

---

## 🖥 UI Plan

### Pages

| Page | Path | Purpose |
|------|------|---------|
| **Home** | `/` | Landing page, project description, quick-start form |
| **Analyze** | `/analyze` | Main analysis form: ticker input, config options, submit |
| **Results** | `/results` | Job status tracker, report viewer, download buttons |
| **History** | `/history` | Past analyses table with links to reports |
| **Settings** | `/settings` | API key config, analysis defaults (dev mode) |

### Components

| Component | Purpose |
|-----------|---------|
| `TickerInput` | Autocomplete ticker search field |
| `AnalysisConfig` | Expandable config form (date range, indicators, report depth) |
| `JobStatusBadge` | Polling status indicator (PENDING / RUNNING / COMPLETE / FAILED) |
| `ReportViewer` | Structured report display with section tabs (Fundamentals / Technical / Risk / Recommendation) |
| `MetricCard` | Small card for individual metrics (P/E, beta, RSI, etc.) |
| `DownloadButton` | Export report as PDF or JSON |

### User Flow

```
1. User opens app → Home page
2. Enters ticker ("AAPL") → clicks "Analyze"
3. Redirected to Results page with run_id in URL
4. Status badge polls backend every 3s
5. Status transitions: PENDING → RUNNING → COMPLETE
6. Report renders with tabs: Executive Summary | Fundamentals | Technical | Sector | Risk | Recommendation
7. User downloads PDF
8. Run appears in History
```

### UI ↔ Backend Contract

- UI calls backend via a `BackendAPIClient` service class (wraps `requests`)
- All API calls through service layer — no direct `requests` calls from pages
- Streamlit session state manages: `run_id`, `current_report`, `history`

---

## 📋 Build Roadmap

### Step-by-Step Execution Plan

```
Phase 2 — Implementation (after approval)

Step 1: Foundation
  ├── Create backend/ and ui/ directory structure
  ├── Extract and adapt shared-platform modules into backend/app/core/
  ├── Set up pyproject.toml / requirements for backend and ui
  └── Configure .env.example

Step 2: Database
  ├── Install SQLAlchemy + Alembic + asyncpg
  ├── Implement all DB models (tickers, analysis_runs, agent_outputs, reports)
  ├── Configure Alembic migrations
  └── Set up pgvector extension initialization

Step 3: Services Layer
  ├── MarketDataService (Yahoo Finance via yfinance)
  ├── FinancialsService (yahoo_fin or Alpha Vantage)
  ├── NewsService (NewsAPI or Tavily)
  └── EmbeddingService (optional, Anthropic/OpenAI embeddings)

Step 4: MCP Tools
  ├── BaseTool interface
  ├── MCPToolGateway with registry
  ├── Implement all 7 tools (price, financials, indicators, sector, risk, news, save_report)
  └── Input/Output Pydantic schemas per tool

Step 5: Agents (CrewAI)
  ├── Install crewai
  ├── Implement ResearchAgent, TechAnalystAgent, SectorAnalystAgent, RiskAnalystAgent, ReportWriterAgent
  ├── Define InvestmentAnalysisCrew with task sequencing
  └── Connect agents to MCP tools via gateway

Step 6: FastAPI Backend
  ├── App factory with lifespan (DB init, tool registry)
  ├── POST /api/v1/analyze (trigger analysis, return run_id)
  ├── GET  /api/v1/analyze/{run_id}/status
  ├── GET  /api/v1/analyze/{run_id}/report
  ├── GET  /api/v1/history
  ├── GET  /health, /ready
  └── Prometheus metrics middleware

Step 7: Streamlit UI
  ├── BackendAPIClient service
  ├── Home, Analyze, Results, History pages
  ├── All components (TickerInput, ReportViewer, etc.)
  └── Polling and session state management

Step 8: Unit Tests
  ├── Tool tests (mock services)
  ├── Service tests (mock HTTP)
  ├── Schema tests
  └── API endpoint tests

Step 9: Docker
  ├── backend.Dockerfile
  ├── ui.Dockerfile
  ├── docker-compose.yml (all 5 services)
  └── Smoke tests against compose stack

Step 10: Integration Tests
  └── Full crew run with docker-compose, assert report generation

Step 11: Kubernetes
  ├── All K8s manifests
  └── Validate with minikube or kind locally

Step 12: Terraform
  ├── GCP modules (GKE, Cloud SQL, Artifact Registry)
  └── Dev environment apply

Step 13: Monitoring
  ├── Prometheus config and alert rules
  └── Grafana dashboards (JSON provisioning)
```

---

## 🧠 Design Decisions Summary

### Why This Architecture

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Async-native, Pydantic integration, fast enough for this workload, excellent OpenAPI docs |
| **CrewAI** | Production-grade agent orchestration, clean crew/agent/task abstraction, active community |
| **Claude Sonnet 4.6** | Strongest reasoning per token for financial analysis; already available in this project context |
| **MCP Tool Pattern** | Enforces clean separation: agents don't own data fetching; tools are testable independently |
| **PostgreSQL + pgvector** | Single DB for structured data and optional vector search; avoids managing separate vector DB |
| **Streamlit** | Fastest path to a working UI for internal/demo use; swap to React only if needed |
| **Prometheus + Grafana** | Industry standard; portable across cloud providers; no vendor lock-in |

### Why These Tools Were Chosen

| Tool | Rationale |
|------|-----------|
| `yfinance` | Free, reliable Yahoo Finance data; sufficient for MVP without paid API costs |
| `sqlalchemy` + `asyncpg` | Async ORM; Alembic gives versioned migrations |
| `pydantic v2` | Fast validation, already in shared-platform |
| `pytest` + `pytest-asyncio` | Standard; handles async testing for FastAPI |
| `pgvector/pgvector:pg16` | Official Docker image with vector extension preinstalled |
| `prometheus-fastapi-instrumentator` | Minimal setup; auto-instruments all FastAPI endpoints |

### What Was Intentionally Excluded

| Item | Reason |
|------|--------|
| ds-ml-skeleton | No ML model training in this system |
| dl-nlp-skeleton | No deep learning workloads |
| React UI | Streamlit is sufficient; React adds frontend build complexity without benefit for this use case |
| LangChain | CrewAI is purpose-built for multi-agent; LangChain would add unnecessary abstraction |
| Celery / Redis | Background tasks handled by FastAPI BackgroundTasks; Celery adds infrastructure complexity not yet justified |
| Separate vector DB (Chroma/Qdrant) | pgvector covers the use case; one less service to operate |
| Feature flags | Premature for this project |
| MLflow / experiment tracking | Not a training pipeline |
| Notebooks (Phase 1–2) | Deferred to Phase 4 per project rules |

---

## ✅ Approval Gate

**Phase 1 is COMPLETE.**

This document covers:
- [x] Full repository audit
- [x] Cleanup plan
- [x] Final architecture design
- [x] Agent definitions
- [x] MCP tool design
- [x] Database design
- [x] Testing strategy
- [x] Infrastructure plan
- [x] Monitoring plan
- [x] UI plan
- [x] Build roadmap
- [x] Design decisions

**DO NOT proceed to Phase 2 without explicit approval.**

Awaiting user sign-off before implementation begins.
