# End-to-End Validation — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Environment:** Docker Compose (local), Python 3.11, PostgreSQL 16 (pgvector image)  
**Backend host port:** 8010 | **UI port:** 8501 | **Prometheus port:** 9090 | **Grafana port:** 3000

---

## System Flow Overview

```
User / UI / Notebook
       │
       ▼
POST /api/v1/analyze
       │  (202 Accepted immediately — run_id returned)
       ▼
Background Thread (ThreadPoolExecutor)
       │
       ├── AnalysisRunRepository.update_status(RUNNING)
       │
       ▼
InvestmentCrew.run()
       │
       ├── [Demo Mode] _run_demo() ──► synthetic report ──► DB ──► COMPLETED
       │
       └── [Live Mode] _run_live()
                  │
                  ├── Research Agent     (stock_price + financial_statements tools)
                  ├── Technical Analyst  (technical_indicators + stock_price tools)
                  ├── Sector Analyst     (sector_analysis + stock_price tools)
                  ├── Risk Analyst       (risk_metrics + news_sentiment tools)
                  └── Report Writer      (save_report tool)
                             │
                             ▼
                     ReportService.save() ──► DB ──► COMPLETED
       │
       ▼
GET /api/v1/analyze/{run_id}/status  (client polls)
GET /api/v1/analyze/{run_id}/report  (once COMPLETED)
```

---

## Success Criteria

| Criterion | Measured By |
|-----------|-------------|
| Analysis submission accepted | POST returns HTTP 202 with run_id |
| Run transitions to RUNNING | Status endpoint shows `running` within 1s |
| Run transitions to COMPLETED | Status endpoint shows `completed` |
| Report persisted to database | Report endpoint returns `200` with content |
| Report contains all 6 required sections | `report_validator.validate_report_sections()` passes |
| History endpoint lists runs | GET /api/v1/analyze returns array with run_id |
| Health and readiness pass | /health → `{"status":"ok"}`, /ready → `{"status":"ok","db":true}` |

---

## Scenario 1 — Demo Mode Analysis (No API Key)

**Context:** ANTHROPIC_API_KEY is a placeholder or DEMO_MODE=true in `.env`.  
**Purpose:** Validate the full submit → poll → report pipeline without a real Anthropic key.

### Setup

```bash
docker compose up -d
curl http://localhost:8010/api/v1/health
# Expected: {"status":"ok","version":"1.0.0"}
```

### Step 1 — Submit Analysis

```bash
curl -s -X POST http://localhost:8010/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","period":"1y"}'
```

**Expected response (HTTP 202):**
```json
{
  "run_id": "f73ebdab-b1cc-43e8-9503-61abdd2636f9",
  "ticker": "AAPL",
  "status": "pending",
  "created_at": "2026-04-20T10:00:00Z"
}
```

**Actual observed:** HTTP 202, run_id returned, status=`pending`.

### Step 2 — Poll Status

```bash
curl -s http://localhost:8010/api/v1/analyze/f73ebdab-b1cc-43e8-9503-61abdd2636f9/status
```

**Expected after ~1 second:**
```json
{
  "run_id": "f73ebdab-b1cc-43e8-9503-61abdd2636f9",
  "ticker": "AAPL",
  "status": "completed",
  "created_at": "2026-04-20T10:00:00Z",
  "started_at": "2026-04-20T10:00:00.3Z",
  "completed_at": "2026-04-20T10:00:00.8Z",
  "error_message": null
}
```

**Actual observed:** Status transitions `pending → running → completed` within approximately 0.5–1 seconds. No errors.

### Step 3 — Retrieve Report

```bash
curl -s http://localhost:8010/api/v1/analyze/f73ebdab-b1cc-43e8-9503-61abdd2636f9/report
```

**Expected:** HTTP 200, `content` field contains markdown report with ⚠️ DEMO MODE header, `structured` JSON contains all 6 sections + `_demo_mode: true`.

**Actual observed:** HTTP 200. Report content includes all required sections:
- Executive Summary
- Fundamental Analysis
- Technical Analysis
- Sector Analysis
- Risk Assessment
- Investment Recommendation

`structured._demo_mode = true` — clearly flagged.

### Step 4 — Verify History

```bash
curl -s http://localhost:8010/api/v1/analyze
```

**Expected:** HTTP 200, `items` array includes the completed run with `has_report: true`.

**Actual observed:** HTTP 200, `{"items":[{...,"status":"completed","has_report":true}],"total":N}`.

**Scenario Result: PASS**

---

## Scenario 2 — Input Validation

**Context:** Testing that the API enforces schema constraints correctly.

### Valid Requests (Accepted)

| Ticker | Period | Expected |
|--------|--------|----------|
| `AAPL` | `1y` | 202 Accepted |
| `MSFT` | `6mo` | 202 Accepted |
| `XOM` | `2y` | 202 Accepted |
| `tsla` (lowercase) | `1y` | 202 Accepted (uppercased internally) |

**Actual observed:** All above returned 202. Ticker is uppercased via `ticker_validator` in the schema.

### Invalid Requests (Rejected)

| Ticker | Period | Expected | Actual |
|--------|--------|----------|--------|
| `""` (empty) | `1y` | 422 — string too short | ✅ 422 |
| `TOOLONGTICKER123` (>10 chars) | `1y` | 422 — string too long | ✅ 422 |
| `AAPL` | `1week` | 422 — not a valid period | ✅ 422 |
| `AAPL` | `""` | 422 — not a valid period | ✅ 422 |

**Scenario Result: PASS**

---

## Scenario 3 — Rate Limiting

**Context:** The POST /api/v1/analyze endpoint is rate-limited to 10 requests/minute per IP.

### Test

```bash
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8010/api/v1/analyze \
    -H "Content-Type: application/json" \
    -d '{"ticker":"AAPL","period":"1y"}'
done
```

**Expected:** First 10 requests return 202. Requests 11–12 return 429 Too Many Requests.

**Actual observed:** Requests 1–10 returned 202. Request 11 returned 429. Rate limiter resets after the 1-minute window.

**Scenario Result: PASS**

---

## Scenario 4 — 404 Handling

**Context:** Accessing resources that do not exist.

| Request | Expected | Actual |
|---------|----------|--------|
| `GET /api/v1/analyze/nonexistent-id/status` | 404 Not Found | ✅ 404 |
| `GET /api/v1/analyze/nonexistent-id/report` | 404 Not Found | ✅ 404 |
| `GET /api/v1/analyze/valid-run-id/report` (run not yet completed) | 202 Accepted (pending) | ✅ 202 |

**Scenario Result: PASS**

---

## Scenario 5 — Concurrent Analysis Runs

**Context:** Multiple runs submitted simultaneously to test ThreadPoolExecutor behavior.

```bash
for ticker in AAPL MSFT XOM; do
  curl -s -X POST http://localhost:8010/api/v1/analyze \
    -H "Content-Type: application/json" \
    -d "{\"ticker\":\"$ticker\",\"period\":\"1y\"}" &
done
wait
```

**Expected:** All 3 runs receive 202 with distinct run_ids. All 3 complete independently.

**Actual observed:** 3 distinct run_ids returned. Each completes in demo mode within ~1 second. History endpoint returns all 3 with `has_report: true`. No DB conflicts observed.

**Scenario Result: PASS**

---

## Observed Edge Cases

| Case | Behavior | Notes |
|------|----------|-------|
| Ticker uppercasing | `tsla` accepted and stored as `TSLA` | Handled by schema validator |
| Report fetch before completion | Returns 202 (not 404) | Correct — run exists but report not yet written |
| History with no runs | Returns `{"items":[],"total":0}` | Correct empty state |
| Placeholder API key | Auto-activates demo mode | `WARNING` logged on startup |
| `DEMO_MODE=true` in env | Demo mode forced regardless of key | Correct |
| Invalid ticker in demo mode | Accepted, demo report generated | Expected — no yfinance call in demo path |
| Invalid ticker in live mode | yfinance raises error → run FAILED | Expected; error_message populated |

---

## Metrics and Observability Validation

**Prometheus:**
```bash
curl -s http://localhost:9090/api/v1/query?query=http_requests_total | jq '.data.result | length'
# Returns > 0 after several requests
```

**FastAPI metrics endpoint:**
```bash
curl -s http://localhost:8010/metrics | grep http_requests_total
# Returns Prometheus text format counters per endpoint + status code
```

**Structured logs (backend):**
```bash
docker logs investment_backend 2>&1 | head -20
# Output is JSONL: {"timestamp":"...","level":"INFO","logger":"...","message":"...","request_id":"..."}
```

All three observed as functional.

---

## Validation Summary

| Scenario | Result |
|----------|--------|
| 1. Demo mode full pipeline | ✅ PASS |
| 2. Input validation | ✅ PASS |
| 3. Rate limiting | ✅ PASS |
| 4. 404 / not-ready handling | ✅ PASS |
| 5. Concurrent runs | ✅ PASS |
| Metrics / observability | ✅ PASS |

**All success criteria met in demo mode. Live mode requires a valid `ANTHROPIC_API_KEY`.**
