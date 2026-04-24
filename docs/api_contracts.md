# API Contracts — Investment MCP Multi-Agent System

**Base URL (Docker Compose):** `http://localhost:8010/api/v1`  
**Interactive docs:** `http://localhost:8010/docs` (Swagger UI)  
**Content-Type:** `application/json` for all POST requests

---

## Authentication

Authentication is **disabled by default** (local development).

To enable: set `API_KEY=<secret>` in `.env`. When enabled, all requests must include:

```
X-API-Key: <your-api-key>
```

Missing or wrong key returns `401 Unauthorized`.

---

## Endpoints

---

### POST /api/v1/analyze

Submit a new stock analysis request. Returns immediately with a `run_id`. Analysis runs in the background.

**Rate limit:** 10 requests per minute per IP address.

#### Request

```json
{
  "ticker": "AAPL",
  "period": "1y",
  "execution_mode": "hybrid"
}
```

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `ticker` | string | 1–10 chars, uppercased automatically | US-listed stock ticker symbol |
| `period` | string | One of: `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y` | Historical data period for analysis |
| `execution_mode` | string | One of: `rag_only`, `agent_only`, `hybrid` (default: `hybrid`) | Analysis execution strategy |

#### Response — 202 Accepted

```json
{
  "run_id": "f73ebdab-b1cc-43e8-9503-61abdd2636f9",
  "ticker": "AAPL",
  "status": "pending",
  "execution_mode": "hybrid",
  "created_at": "2026-04-20T10:00:00.123456Z"
}
```

#### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 422 | Invalid ticker length or invalid period value | `{"detail": [{"type":"...", "msg":"..."}]}` |
| 429 | Rate limit exceeded | `{"detail": "Rate limit exceeded: 10 per 1 minute"}` |
| 401 | API key required but missing or wrong | `{"detail": "Unauthorized"}` |

#### Example

```bash
curl -s -X POST http://localhost:8010/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker":"MSFT","period":"6mo"}'
```

---

### GET /api/v1/analyze/{run_id}/status

Poll the status of an analysis run.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `run_id` | UUID string | Returned by POST /analyze |

#### Response — 200 OK

```json
{
  "run_id": "f73ebdab-b1cc-43e8-9503-61abdd2636f9",
  "ticker": "AAPL",
  "status": "completed",
  "created_at": "2026-04-20T10:00:00.123456Z",
  "started_at": "2026-04-20T10:00:00.345678Z",
  "completed_at": "2026-04-20T10:00:01.234567Z",
  "error_message": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | UUID of the analysis run |
| `ticker` | string | Uppercase ticker symbol |
| `status` | string | One of: `pending`, `running`, `completed`, `failed` |
| `execution_mode` | string \| null | Execution mode used for this run |
| `created_at` | ISO 8601 datetime | When run was submitted |
| `started_at` | ISO 8601 datetime \| null | When crew began processing |
| `completed_at` | ISO 8601 datetime \| null | When run finished (success or failure) |
| `error_message` | string \| null | Human-readable error if status is `failed` |

#### Status Lifecycle

```
pending → running → completed
                 ↘ failed
```

#### Error Responses

| Status | Condition |
|--------|-----------|
| 404 | run_id does not exist |
| 401 | API key required but missing |

#### Example

```bash
curl -s http://localhost:8010/api/v1/analyze/f73ebdab-b1cc-43e8-9503-61abdd2636f9/status
```

---

### GET /api/v1/analyze/{run_id}/report

Retrieve the completed analysis report.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `run_id` | UUID string | Returned by POST /analyze |

#### Response — 200 OK (report ready)

```json
{
  "report_id": "a1b2c3d4-...",
  "run_id": "f73ebdab-...",
  "ticker": "AAPL",
  "content": "# Investment Analysis Report: AAPL\n\n## Executive Summary\n...",
  "structured": {
    "ticker": "AAPL",
    "executive_summary": "...",
    "fundamentals": "...",
    "technical_analysis": "...",
    "sector_context": "...",
    "risk_profile": "...",
    "recommendation": "...",
    "_demo_mode": true
  },
  "execution_mode": "hybrid",
  "created_at": "2026-04-20T10:00:01.234567Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | string | UUID of the report record |
| `run_id` | string | UUID of the parent analysis run |
| `ticker` | string | Uppercase ticker symbol |
| `content` | string | Full markdown report text |
| `structured` | object | Parsed sections from the report |
| `structured._demo_mode` | boolean | `true` if generated in demo mode |
| `execution_mode` | string \| null | Execution mode that produced this report |
| `created_at` | ISO 8601 datetime | When report was saved |

#### Response — 202 Accepted (run not yet complete)

Returned when the run exists but has not yet produced a report (status is `pending` or `running`).

```json
{
  "detail": "Analysis not yet complete"
}
```

#### Error Responses

| Status | Condition |
|--------|-----------|
| 202 | Run exists but not yet completed |
| 404 | run_id does not exist, or run failed with no report |
| 401 | API key required but missing |

#### Example

```bash
curl -s http://localhost:8010/api/v1/analyze/f73ebdab-b1cc-43e8-9503-61abdd2636f9/report \
  | jq '.structured.recommendation'
```

---

### GET /api/v1/analyze

List recent analysis runs, most recent first.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Maximum number of runs to return |

#### Response — 200 OK

```json
{
  "items": [
    {
      "run_id": "f73ebdab-b1cc-43e8-9503-61abdd2636f9",
      "ticker": "AAPL",
      "status": "completed",
      "execution_mode": "hybrid",
      "created_at": "2026-04-20T10:00:00.123456Z",
      "completed_at": "2026-04-20T10:00:01.234567Z",
      "has_report": true
    },
    {
      "run_id": "c2b0117a-...",
      "ticker": "MSFT",
      "status": "failed",
      "execution_mode": "rag_only",
      "created_at": "2026-04-20T09:55:00Z",
      "completed_at": "2026-04-20T09:55:10Z",
      "has_report": false
    }
  ],
  "total": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | List of HistoryItem objects |
| `total` | integer | Number of items returned (≤ limit) |
| `items[].execution_mode` | string \| null | Execution mode used for this run |
| `items[].has_report` | boolean | Whether a report was successfully generated for this run |

#### Error Responses

| Status | Condition |
|--------|-----------|
| 401 | API key required but missing |

#### Example

```bash
curl -s "http://localhost:8010/api/v1/analyze?limit=5"
```

---

### GET /api/v1/health

Lightweight liveness check. Returns immediately without database queries.

#### Response — 200 OK

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### Example

```bash
curl -s http://localhost:8010/api/v1/health
```

---

### GET /api/v1/ready

Readiness check. Verifies database connectivity and MCP tool registration. Use this to determine whether the backend is ready to accept analysis requests.

#### Response — 200 OK

```json
{
  "status": "ok",
  "db": "ok",
  "mcp_tools": [
    "get_stock_price",
    "get_financial_statements",
    "get_technical_indicators",
    "get_sector_analysis",
    "get_risk_metrics",
    "get_news_sentiment"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ok"` if all checks pass |
| `db` | string | `"ok"` if database connection is healthy; `"error"` if it failed |
| `mcp_tools` | string[] | List of registered MCP tool names (6 data tools) |

#### Example

```bash
curl -s http://localhost:8010/api/v1/ready | jq '.db'
```

---

### GET /api/v1/sources

List all configured data sources with their current status and last-fetch metadata. Does not require authentication.

#### Response — 200 OK

```json
{
  "sources": [
    {
      "key": "yahoo_finance",
      "name": "Yahoo Finance",
      "status": "OK",
      "description": "Price history, financials, company info via yfinance",
      "asset_types": "equities",
      "last_fetch": "2026-04-24T10:00:01.123456Z",
      "latency_ms": 312.4,
      "records_returned": 252,
      "assets_covered": 0,
      "notes": "Provides price history, financial statements, technical data, sector ETFs",
      "error_message": ""
    },
    {
      "key": "newsapi",
      "name": "News API",
      "status": "WARN",
      "description": "Financial news headlines via newsapi.org",
      "asset_types": "news",
      "last_fetch": null,
      "latency_ms": 0.0,
      "records_returned": 0,
      "assets_covered": 0,
      "notes": "Key not configured — using keyword sentiment fallback",
      "error_message": ""
    }
  ],
  "summary": {
    "total": 5,
    "by_status": {"OK": 1, "WARN": 1, "OFFLINE": 1, "FUTURE": 2}
  }
}
```

| Status Value | Meaning |
|-------------|---------|
| `OK` | Source is reachable and returning data |
| `WARN` | Source is degraded or using a fallback |
| `ERROR` | Last fetch failed with an error |
| `OFFLINE` | Source is configured but not active |
| `FUTURE` | Source is planned but not implemented |

#### Example

```bash
curl -s http://localhost:8010/api/v1/sources | jq '.summary'
```

---

### GET /api/v1/sources/status

Compact health summary of all data sources grouped by status count.

#### Response — 200 OK

```json
{
  "total": 5,
  "by_status": {
    "OK": 1,
    "WARN": 1,
    "OFFLINE": 1,
    "FUTURE": 2
  }
}
```

#### Example

```bash
curl -s http://localhost:8010/api/v1/sources/status
```

---

### GET /metrics

Prometheus metrics endpoint. Returns OpenMetrics text format. Not versioned under `/api/v1`.

**URL:** `http://localhost:8010/metrics`

**Example metrics exposed:**
- `http_requests_total{method, handler, status_code}` — Request counter per endpoint
- `http_request_duration_seconds{method, handler}` — Request latency histogram
- Python runtime metrics (GC, memory, threads)

---

## Common Error Response Shapes

### Validation Error (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "ticker"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Application Error (4xx / 5xx)

```json
{
  "detail": "Analysis run not found"
}
```

### Rate Limit Error (429)

```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

---

## Analysis Period Values

| Value | Meaning |
|-------|---------|
| `1mo` | 1 month of historical data |
| `3mo` | 3 months |
| `6mo` | 6 months |
| `1y` | 1 year (default) |
| `2y` | 2 years |
| `5y` | 5 years |

---

## Execution Mode Values

| Value | LLM Calls | Description | Typical Duration |
|-------|-----------|-------------|-----------------|
| `rag_only` | No | Fetches raw market data from all 6 tools and returns a formatted snapshot report. No AI synthesis. | ~2–5 seconds |
| `agent_only` | Yes | Runs all 5 CrewAI agents sequentially. Each agent calls tools on demand. Full AI-generated investment memo. | ~30–60 seconds |
| `hybrid` | Yes | Pre-fetches all data via RAG pass, then injects that data into the agent crew. Default mode. | ~40–70 seconds |

When `DEMO_MODE=true` or `ANTHROPIC_API_KEY` is a placeholder, all modes return a synthetic demo report with no LLM calls (~1 second).

---

## Polling Pattern

Since analysis is asynchronous, clients should poll the status endpoint:

```python
import time, requests

BASE = "http://localhost:8010/api/v1"

# Submit
resp = requests.post(f"{BASE}/analyze", json={"ticker": "AAPL", "period": "1y", "execution_mode": "hybrid"})
run_id = resp.json()["run_id"]

# Poll until done
while True:
    status = requests.get(f"{BASE}/analyze/{run_id}/status").json()
    if status["status"] in ("completed", "failed"):
        break
    time.sleep(5)

# Fetch report
if status["status"] == "completed":
    report = requests.get(f"{BASE}/analyze/{run_id}/report").json()
    print(report["content"])
```

**Typical durations:**
- Demo mode: ~0.5–1 second (any execution_mode with placeholder API key)
- `rag_only` live: ~2–5 seconds
- `agent_only` live: ~30–60 seconds
- `hybrid` live: ~40–70 seconds
