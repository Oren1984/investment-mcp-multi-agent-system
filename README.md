# Oren Salami | 🧠 AI Systems Engineer

## Intelligent Systems • AI Agents • Data & Automation

---

# 🧠 Investment MCP Multi-Agent System

A production-grade multi-agent AI system for equity research automation.

This project uses five specialized CrewAI agents, a structured MCP tool gateway, FastAPI backend services, Streamlit UI, PostgreSQL with pgvector, observability, and cloud-native infrastructure foundations to generate multi-section investment analysis reports from a single stock ticker.

---

## 🧠 Project Overview

The **Investment MCP Multi-Agent System** is an AI-powered equity research platform designed to automate structured investment analysis.

The system receives a stock ticker and coordinates multiple specialized agents to collect market data, analyze fundamentals, inspect technical indicators, compare sector positioning, calculate risk metrics, and synthesize the results into a structured investment report.

The architecture is based on a clear separation between agents, tools, services, API routes, database persistence, UI, monitoring, and infrastructure.

The system supports full agent execution, data-only RAG-style execution, and hybrid execution that pre-fetches market context before running the agent workflow.

---

## 🎯 Purpose

The purpose of this project is to demonstrate:

- How to design a production-grade multi-agent AI system
- How to structure financial analysis using specialized CrewAI agents
- How to decouple agent logic from service implementation using an MCP tool gateway
- How to combine FastAPI, Streamlit, PostgreSQL, pgvector, Prometheus, and Grafana
- How to support multiple execution modes for different runtime needs
- How to prepare an AI system for Docker, Kubernetes, and Terraform-based deployment
- How to document, test, validate, and present an AI system as a portfolio-ready project

---

## 🚀 Core Capabilities

- Five specialized CrewAI agents
- Sequential multi-agent investment workflow
- MCP Gateway with validated tool execution
- Stock price analysis
- Financial statement retrieval
- Technical indicator analysis
- Sector comparison
- Risk metric calculation
- News sentiment analysis
- Structured report generation
- FastAPI backend
- Streamlit UI with four pages
- PostgreSQL 16 with pgvector
- Alembic migrations
- Prometheus metrics
- Grafana dashboards
- Docker Compose orchestration
- Kubernetes and Terraform infrastructure foundation
- Multiple execution modes: Hybrid, RAG Only, Agent Only
- 210 automated tests across unit, integration, E2E, and smoke layers

---

## 🧱 Architecture & System Design

The system is designed as a modular AI platform with clear separation between orchestration, tools, backend services, persistence, UI, observability, and infrastructure.

```text
investment-mcp-multi-agent-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI route handlers
│   │   ├── crews/          # InvestmentCrew, tasks, execution modes
│   │   ├── mcp/            # MCPGateway, MCPRegistry, tool classes
│   │   ├── services/       # MarketData, Financials, Risk, News, LLM, Report
│   │   ├── db/             # Models, repositories, Alembic migrations
│   │   └── schemas/        # Pydantic request/response models
│   └── tests/              # Unit, integration, E2E, smoke tests
├── ui/app/                 # Streamlit pages
├── infra/                  # Docker, Kubernetes, Terraform
├── monitoring/             # Prometheus config and Grafana dashboards
├── notebooks/              # Demo walkthroughs and technical scenarios
├── docs/                   # API contracts, runbook, QA audit, testing matrix
├── static-site/            # Portfolio landing page
└── docker-compose.yml
```

The architecture is intentionally separated into independent layers so the system remains maintainable, testable, observable, and ready for future production deployment.

---

## 🛠️ Tech Stack

- LayerTechnologies
- OrchestrationCrewAI, sequential multi-agent process
- Backend APIFastAPI, Pydantic v2, async routes, rate limiting
- LLMAnthropic Claude
- Tool ProtocolMCP Gateway, Pydantic-validated tool inputs
- Market Datayfinance, NewsAPI
- DatabasePostgreSQL 16, pgvector, Alembic
- UIStreamlit
- ObservabilityPrometheus, Grafana, structured JSON logging
- InfrastructureDocker Compose, Kubernetes, Terraform, GCP-ready design
- TestingPytest, unit tests, integration tests, E2E tests, smoke tests
- DocumentationMarkdown docs, notebooks, static portfolio site

---

## 🤖 Agents

The system includes five specialized agents.

| Agent | Responsibility | MCP Tools |
|-------|----------------|-----------|
| Research Agent | Market data, fundamentals, news | get_stock_price, get_financial_statements, get_news_sentiment |
| Technical Analyst | Price indicators and trend signals | get_stock_price, get_technical_indicators |
| Sector Analyst | Industry positioning and ETF comparison | get_sector_analysis |
| Risk Analyst | Volatility, drawdown, Sharpe ratio, Va | get_risk_metrics |
| Report Writer | Synthesizes all prior outputs into a structured report | save_report |

Agents execute sequentially.

The Report Writer receives all previous task outputs as context before producing the final investment report.

---

## 🔀 Execution Modes

The system supports three execution modes.

| Mode | Behavior |
|------|----------|
| hybrid | Default mode. Pre-fetches all market data through execute_rag_pass(), then runs the full agent pipeline with data in context |
| rag_only | Fetches data only, without an LLM call. Returns a structured snapshot report quickly |
| agent_only | Runs the full CrewAI pipeline. Agents call MCP tools on demand |

This design allows the same backend to support demo usage, faster data-only workflows, and full agentic analysis.

---

## 🧩 MCP Tool Gateway

The MCP Gateway decouples agent logic from service implementations.

Every tool call is validated through a Pydantic input schema before execution.

- get_stock_price             → MarketDataService
- get_financial_statements    → FinancialsService
- get_technical_indicators    → RiskService
- get_risk_metrics            → RiskService
- get_news_sentiment          → NewsService
- get_sector_analysis         → MarketDataService
- save_report                 → ReportService

execute_rag_pass() calls all data tools in one pass with per-tool failure isolation.

This means one failing tool does not abort the full pre-fetch process.

---

## 📦 Repository Structure

backend/
├── app/
│   ├── api/routes/       # API route handlers
│   ├── crews/            # CrewAI orchestration and execution modes
│   ├── mcp/              # MCP gateway, registry, and tool classes
│   ├── services/         # Market, financials, risk, news, LLM, report services
│   ├── db/               # Database models, repositories, migrations
│   └── schemas/          # Pydantic schemas
│
└── tests/                # Unit, integration, E2E, and smoke tests

ui/app/
└── Streamlit application pages

infra/
└── Docker, Kubernetes, and Terraform infrastructure

monitoring/
└── Prometheus and Grafana configuration

notebooks/
└── Demo walkthroughs and technical reviewer notebooks

docs/
└── API contracts, runbook, QA audit, testing matrix, and limitations

static-site/
└── Portfolio landing page and interactive static demo

---

## 🚀 How to Run
1. Create environment file
```bash
cp .env.example .env
```

Required for full LLM execution:

ANTHROPIC_API_KEY=your_key_here

Optional:

API_KEY=your_api_key
NEWS_API_KEY=your_news_api_key

2. Start the system
```bash
docker compose up --build
```

3. Open services
ServiceURL
Streamlit UIhttp://localhost:8501

FastAPI Docshttp://localhost:8000/docs

Prometheushttp://localhost:9090

Grafanahttp://localhost:3000

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/analyze | POST | Submit analysis request with ticker, period, and execution_mode |
| /api/v1/analyze/{id}/status | GET | Poll run status |
| /api/v1/analyze/{id}/report | GET | Retrieve completed report |
| /api/v1/analyze | GET | Retrieve analysis history |
| /api/v1/sources | GET | Data provider status |
| /api/v1/sources/status | GET | Aggregated source health summary |
| /api/v1/health | GET | Health check |
| /api/v1/ready | GET | Readiness check and tool registration confirmation |
| /api/v1/metrics | GET | Prometheus metrics |

Authentication uses the X-API-Key header when the API_KEY environment variable is configured.

POST /api/v1/analyze is rate-limited to 10 requests per minute per IP.

---

## 🧪 Testing

Run tests from the backend directory:
```bash
cd backend
pip install -r requirements.txt
pytest
```

Test coverage summary:

- LayerFilesTests
- Unit10134
- Integration552
- E2E15
- Smoke219
- Total18210

The automated test suite uses in-memory SQLite with StaticPool and FastAPI dependency_overrides for database and gateway isolation.

External network calls are not required in the test suite.

---

## 📊 Observability

The project includes an observability foundation for production-style monitoring.

Prometheus scrapes /metrics every 15 seconds
Metrics include request counts, latency histograms, and Python process metrics
Grafana dashboard is auto-provisioned from monitoring/grafana/dashboards/overview.json
Structured JSON logs carry run_id
ContextVar propagation is used through executor threads with copy_context()

---

## 📚 Documentation

This project includes a documentation suite focused on API clarity, operational readiness, QA, and known limitations.

| File | Contents |
|------|----------|
| docs/api_contracts.md | Endpoint contracts with request and response schemas |
| docs/runbook.md | Deployment, configuration, and troubleshooting |
| docs/testing_matrix.md | Complete test inventory and component coverage |
| docs/qa_audit.md | QA audit with bugs found and fixed |
| docs/known_limitations.md | Detailed limitations and mitigation notes |

---

## 📓 Demo Assets
| Asset | Purpose |
|-------|---------|
| notebooks/01_demo_walkthrough.ipynb | End-to-end user flow walkthrough |
| notebooks/02_technical_architecture.ipynb | Engineering deep dive for technical reviewers |
| notebooks/03_demo_scenarios.ipynb | Stock scenarios and risk metric interpretation |
| static-site/index.html | Portfolio landing page with interactive demo |

---

## 🌐 Portfolio Demo

This project includes a static portfolio presentation layer.

The portfolio demo is designed to show:

- Multi-agent investment workflow
- MCP Gateway architecture
- Execution modes
- Tool-based financial analysis
- API and service separation
- Testing and observability maturity
- Production-readiness mindset

The demo is suitable for instructors, technical reviewers, recruiters, and portfolio presentation.

---

## 🧩 What This Project Demonstrates

This project demonstrates my ability to:

- Design multi-agent AI systems
- Build MCP-style tool gateways
- Separate AI orchestration from service implementations
- Structure FastAPI backend systems
- Integrate Streamlit as a practical AI UI
- Use PostgreSQL and pgvector as a production-ready data foundation
- Add observability with Prometheus and Grafana
- Prepare infrastructure for Docker, Kubernetes, Terraform, and GCP
- Build a tested and documented AI system
- Present complex AI architecture clearly as part of a professional portfolio

---

## 📌 Current Status

Status: Portfolio-ready / Tested / Production-minded architecture

This project is considered complete for portfolio presentation.

Future changes should be limited to:

- Small UI polish
- Documentation alignment
- Static site updates
- Minor bug fixes
- Optional deployment improvements

The current portfolio version does not require additional paid integrations beyond optional live LLM or market-data keys.

---

## ⚠️ Known Limitations

- In-process SourceRegistry and rate limiter are not shared across replicas
- Multi-pod deployments should use Redis-backed alternatives
- No RBAC is implemented
- Authentication is based on a single API key
- There is no per-user audit trail
- yfinance reliability may vary for small-cap, OTC, or very recent IPO assets
- LLM calls are not included in the automated test suite because they require a live Anthropic API key
- This project is not financial advice and should not be used for real investment decisions

---

## 🏁 Final Note

This project is part of my AI Engineering portfolio.

It represents a production-minded multi-agent AI system that combines CrewAI orchestration, MCP tool architecture, FastAPI services, database persistence, observability, testing, documentation, and portfolio-ready presentation.

The goal is not only to analyze investment data, but to demonstrate how intelligent AI systems can be designed, validated, documented, and prepared for real-world deployment.

---

## 📄 License

This project is licensed under the MIT License.
See the LICENSE file for details.

---
