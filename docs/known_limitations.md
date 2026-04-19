# Known Limitations — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Tone:** Engineering-honest. These limitations are documented so evaluators, users, and future contributors understand exactly what the system does and does not do.

---

## Data Limitations

### 1. Market Data Source: yfinance Only

All market data (price history, financial statements, company info, technical indicators, sector data, risk metrics) is sourced exclusively from [yfinance](https://pypi.org/project/yfinance/), which is an unofficial Yahoo Finance scraper.

**Implications:**
- **Reliability:** Yahoo Finance can change its API without notice. yfinance may break between versions.
- **Latency:** Data is typically delayed 15–20 minutes for real-time price data.
- **Coverage:** Primarily covers US-listed equities (NYSE, NASDAQ). Non-US tickers may return incomplete or missing data.
- **Historical depth:** Dependent on Yahoo Finance's data availability per ticker. Delisted or very new tickers may have limited history.
- **Rate limiting:** Excessive yfinance calls can trigger Yahoo Finance throttling. No caching layer is implemented.

### 2. News Sentiment: Keyword-Based Only

When `NEWS_API_KEY` is not set (the default), news sentiment falls back to a basic positive/negative keyword-matching algorithm in `news_service.py`. This is not a machine-learning model or NLP-based sentiment analysis.

**Implications:**
- Sentiment labels (`POSITIVE`, `NEGATIVE`, `NEUTRAL`) are coarse approximations.
- Sarcasm, negation, and context are not handled.
- Headline count and recency are not factored into the sentiment score.
- Even with a `NEWS_API_KEY`, the sentiment algorithm is still the basic keyword matcher — the API only improves headline sourcing.

### 3. Alpha Vantage Key Not Used

`ALPHA_VANTAGE_KEY` is present in the config and `.env` but no production code currently calls Alpha Vantage APIs. The key is a dead configuration value.

### 4. No Data Caching

Each analysis run fetches fresh data from yfinance for every tool call. There is no caching layer (Redis, in-memory, or file-based). This means:
- Repeated analysis of the same ticker fetches data multiple times.
- Under high load, yfinance may be throttled.
- Network failures during tool calls cause the agent task (and the run) to fail.

### 5. Ticker Symbol Validation Is Deferred to yfinance

The API schema accepts any string of 1–10 characters and uppercases it. Invalid tickers (e.g., `"GOOGLE"` instead of `"GOOGL"`) pass schema validation but fail when yfinance cannot find the ticker. In live mode, the run enters `FAILED` status. In demo mode, any ticker string is accepted (no yfinance calls are made).

---

## LLM / AI Limitations

### 6. Single LLM Provider: Anthropic Only

The system is hardcoded to use Anthropic's Claude via LiteLLM (through CrewAI). There is no abstraction for swapping to other providers (OpenAI, Gemini, local models). Changing providers would require modifying `llm_service.py` and `investment_crew.py`.

### 7. No Agent Memory or State Persistence

Each analysis run starts a fresh CrewAI crew with no memory of previous runs. Agents do not learn from past analyses. There is no vector search or long-term context despite pgvector being installed.

### 8. No Retry Logic for LLM Failures

If an LLM call fails (network error, rate limit, timeout), the agent task fails and the entire crew fails. The run is marked `FAILED`. There is no retry-with-backoff for individual agent tasks.

### 9. Analysis Quality Depends on Agent Prompt Quality

The quality of the output report depends on:
- The instruction prompts in `crews/tasks.py`
- The LLM's ability to interpret yfinance data
- The yfinance data completeness for the given ticker

Poorly-formatted yfinance output or hallucination by the LLM can result in incorrect or incomplete analysis sections. The system does not validate the factual accuracy of agent-generated content.

### 10. Demo Mode Reports Are Fully Synthetic

Demo mode reports contain entirely placeholder numbers and analysis (`P/E Ratio: 28.3x`, `Beta: 1.18`, etc.). These values are not derived from real data and are identical regardless of the ticker submitted. They exist solely to demonstrate report structure and API flow.

---

## Analysis Limitations

### 11. Report Section Validation Is Structural, Not Substantive

`report_validator.py` checks that 6 section headers exist in the markdown report:
- Executive Summary
- Fundamental Analysis
- Technical Analysis
- Sector Analysis
- Risk Assessment
- Recommendation (or Investment Recommendation)

It does not validate that sections contain meaningful content. A report with empty or placeholder sections would pass validation.

### 12. Technical Indicators Are Calculated from Daily Close Prices

All technical indicators (RSI, MACD, Bollinger Bands, SMA, EMA) are calculated from daily OHLCV data from yfinance. Intraday signals, weekly/monthly aggregations, or tick-level data are not used.

### 13. Sector Comparison Is Simple 1-Year Return Delta

The sector analysis compares the ticker's 1-year return against a sector ETF (e.g., XLK for Technology). This is a simple relative return comparison. No style factor analysis, beta-adjusted comparison, or peer group analysis is performed.

### 14. Risk Metrics Use Historical Data Only

Beta, volatility, VaR, and Sharpe ratio are calculated from historical daily returns. These are backward-looking metrics. Forward-looking risk (earnings estimates, analyst revisions, options-implied volatility) is not computed.

---

## Missing Features

### 15. No User Authentication Beyond API Key

The system supports a single shared `API_KEY` for all callers. There is no user registration, session management, or per-user run history. All runs are visible to all callers.

### 16. No Analysis History Per Ticker Beyond Simple Listing

`GET /api/v1/analyze` returns the 20 most recent runs across all tickers. There is no endpoint to retrieve all historical analyses for a specific ticker with filtering or pagination beyond the `limit` parameter.

### 17. No Webhook or Push Notification for Run Completion

Clients must poll `GET /api/v1/analyze/{run_id}/status` to detect completion. There is no WebSocket connection, Server-Sent Events stream, or webhook callback support.

### 18. No Report Comparison or Historical Trend Analysis

The UI and API do not provide a view comparing multiple analyses of the same ticker over time. The `ReportRepository.list_by_ticker()` method exists in the codebase but is not exposed via any API endpoint.

### 19. No Portfolio-Level Analysis

The system analyzes one ticker per request. There is no multi-ticker portfolio view, correlation analysis, or portfolio-level risk aggregation.

### 20. Kubernetes and Terraform Not Implemented

The `k8s/` and `terraform/` directories exist in the repository but are empty. There are no Kubernetes manifests, Helm charts, or Terraform modules for cloud deployment.

---

## Infrastructure and Operational Limitations

### 21. Background Jobs Not Durable

Analyses run in a `ThreadPoolExecutor`. If the backend container restarts while a run is in progress, the run remains permanently in `RUNNING` status. There is no job recovery mechanism, dead letter queue, or TTL for stuck runs.

### 22. Rate Limiter Is Not Distributed

SlowAPI's rate limiter uses in-memory counters. Running more than one backend replica would give each instance its own independent counter, effectively multiplying the rate limit by the number of replicas. Redis-backed rate limiting is not configured.

### 23. No TLS / HTTPS

The system does not configure TLS termination. All traffic between client and API is unencrypted unless a reverse proxy is placed in front. This is not suitable for exposing over the public internet.

### 24. CORS Is Wildcard

`allow_origins=["*"]` is set in `main.py`. This is acceptable for local development and demos but allows any origin to make cross-origin requests to the API in a deployed environment.

### 25. No Automated Database Backups

PostgreSQL data is stored in a Docker volume. No backup schedule, point-in-time recovery, or export mechanism is configured. Data loss occurs on `docker compose down -v`.

---

## This Is Not Financial Advice

The outputs of this system — whether in demo mode or live AI mode — are generated by automated software and do not constitute financial advice, investment recommendations, or analysis suitable for making real investment decisions.

All analysis is based on publicly available data from Yahoo Finance, processed by AI models that can and do make errors, hallucinate, and misinterpret data. No human financial analyst has reviewed the outputs.

**Do not use this system's outputs to make real investment decisions.**
