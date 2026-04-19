# Production Readiness Assessment — Investment MCP Multi-Agent System

**Date:** 2026-04-20  
**Assessor:** Engineering / DevOps Lead  
**Current deployment target:** Single-host Docker Compose  
**Assessment scope:** Backend API, database, agents, infrastructure, security, observability

---

## Summary

This system is **demo/portfolio-ready** and can run reliably in a single-host Docker environment. It is **not production-ready** in the sense of a multi-tenant, horizontally-scaled, SLA-backed service. The gaps are structural (missing secrets management, in-memory state, no CI/CD pipeline) rather than functional.

---

## Capability Assessment

### Ready

| Capability | Evidence |
|------------|----------|
| API accepts analysis requests asynchronously | ThreadPoolExecutor + 202 Accepted pattern |
| Runs tracked in PostgreSQL with status transitions | AnalysisRun model with PENDING→RUNNING→COMPLETED→FAILED |
| Reports persisted and retrievable | Report model, ReportRepository, GET /report endpoint |
| Demo mode without API key | `is_demo_mode()` + `_run_demo()` synthetic report path |
| Structured JSON logging | `JSONFormatter` with request_id and run_id context propagation |
| Prometheus metrics | `prometheus-fastapi-instrumentator` on all endpoints |
| Grafana dashboards | `infra/monitoring/` with provisioned datasource and dashboards |
| Docker Compose single-host deployment | All 5 services (postgres, backend, ui, prometheus, grafana) |
| Rate limiting on analysis endpoint | SlowAPI, 10/minute per IP |
| Optional API key authentication | X-API-Key header, disabled when `API_KEY` env var is empty |
| Input validation and error responses | Pydantic schemas, custom AppError hierarchy |
| Health and readiness endpoints | `/health` and `/ready` with DB and MCP tool checks |
| Correlation ID request tracing | Middleware generates/propagates X-Request-ID |
| Alembic migration support | `USE_ALEMBIC=true` runs `alembic upgrade head` on startup |

### Partially Ready

| Capability | Gap | Effort to Close |
|------------|-----|-----------------|
| Secrets management | `.env` file on disk; no Vault, SSM, or K8s secrets | Medium |
| Database connection pooling | Pool size configurable (default 10+5 overflow); no pgBouncer | Low |
| Background job reliability | ThreadPoolExecutor — jobs lost if container restarts mid-run | Medium |
| Report section validation | Header presence check only; no content depth validation | Low |
| News sentiment | Basic positive/negative word matching; not NLP-grade | Medium |
| Multi-agent error recovery | If one agent task fails, the whole crew fails; no task-level retry | Medium |
| Container image hardening | Base image is `python:3.11-slim` (reasonable); no SBOM, no image signing | Low |
| Database migrations in production | Alembic support exists but `USE_ALEMBIC=false` by default | Low |

### Not Ready

| Capability | Notes |
|------------|-------|
| Horizontal scaling | Rate limiter is in-memory; sessions and background jobs are single-instance |
| Kubernetes deployment | `k8s/` directory exists but is empty |
| Terraform / cloud provisioning | `terraform/` directory exists but is empty |
| CI/CD pipeline | No GitHub Actions, no automated test + build + push workflow |
| Secrets rotation | No mechanism for rotating API keys without container restart |
| Multi-tenant isolation | No user/tenant concept; all runs share one DB schema |
| Audit logging | Request logs exist; no immutable audit trail for compliance |
| Backup and recovery | No automated DB backup configured |
| SLA / uptime monitoring | Prometheus + Grafana present but no alerting rules configured |
| pgvector usage | Extension installed but no vector columns or similarity search implemented |

---

## Reliability

### Failure Modes

| Failure | Current Behavior | Production Expectation |
|---------|-----------------|----------------------|
| Backend container restart mid-run | Run stuck in RUNNING state forever | Job queue with at-least-once delivery |
| PostgreSQL unavailable | FastAPI health returns unhealthy; new requests fail | Retry with backoff; read replicas |
| Anthropic API 429 (rate limit) | Run marked FAILED with LiteLLM error | Retry with exponential backoff |
| yfinance data unavailable | MCP tool returns error dict; agent may recover or fail | Cache layer; fallback data source |
| ThreadPoolExecutor exhausted (>5 concurrent) | Queue blocks; new jobs wait | Dedicated task queue (Celery/Redis) |

### Recovery

- **Database reconnects** on next request (SQLAlchemy pool handles transient disconnects).
- **Stuck runs** in RUNNING state have no TTL mechanism. Manual intervention required to reset.
- **Demo mode** provides a complete fallback when the LLM provider is unavailable.

---

## Security

### Current State

| Control | Status | Notes |
|---------|--------|-------|
| API key authentication | Optional, disabled by default | Enable via `API_KEY` env var |
| HTTPS / TLS termination | Not configured | Requires reverse proxy (nginx/traefik) |
| CORS policy | Wildcard (`allow_origins=["*"]`) | Must be restricted for production |
| Secrets in environment variables | Yes (`.env` file) | Not suitable for production secret storage |
| SQL injection | Not possible | SQLAlchemy ORM with parameterized queries |
| Input length limits | Enforced by Pydantic schemas (ticker: 1–10 chars) | Adequate |
| Rate limiting | 10 req/min per IP on analyze endpoint | Configurable via `RATE_LIMIT_ANALYZE` |
| Container runs as root | Not confirmed | Should run as non-root user |

### Hardening Steps Required for Production

1. Enable HTTPS via reverse proxy (nginx, traefik, or cloud load balancer).
2. Restrict CORS to specific frontend origin.
3. Move secrets to a proper secrets manager (AWS SSM, HashiCorp Vault, K8s secrets).
4. Set a strong `API_KEY` value.
5. Run containers as non-root user (add `USER 1000` to Dockerfiles).
6. Replace wildcard CORS with explicit origin allowlist.

---

## Scalability

### Single-Instance Limits

| Resource | Current Limit | Scaling Path |
|----------|--------------|-------------|
| Concurrent analyses | 5 (configurable `MAX_CONCURRENT_RUNS`) | Celery + Redis workers |
| API requests | Uvicorn async (handles hundreds of concurrent connections) | Add replicas behind load balancer |
| Rate limiting | Per-instance in-memory | Redis-backed SlowAPI |
| Database connections | 10 pool + 5 overflow per backend instance | pgBouncer for connection multiplexing |

### Data Volume

- Each analysis run produces one Report row (~5–20 KB of markdown text + structured JSON).
- At 1000 runs/day, storage grows ~5–20 MB/day. PostgreSQL handles this trivially.
- No archival or retention policy is implemented.

---

## Observability

| Signal | Implementation | Gap |
|--------|---------------|-----|
| Metrics | Prometheus scraping `/metrics` (endpoint counters, latency histograms) | No SLO alerting rules |
| Logs | JSON structured logs per request and per run | No centralized log aggregation (e.g. Loki) |
| Traces | Correlation ID header propagated through logs | No distributed tracing (no OpenTelemetry) |
| Dashboards | Grafana provisioned at port 3000 | No dashboard content confirmed for custom metrics |
| Alerting | Not configured | No Alertmanager rules |

---

## Deployment Readiness by Target

| Target | Ready | Notes |
|--------|-------|-------|
| Local development (bare Python) | ✅ | `cd backend && uvicorn app.main:app` |
| Docker Compose (single host) | ✅ | `docker compose up -d` — all services healthy |
| Docker Compose (with real API key) | ✅ | Set `ANTHROPIC_API_KEY` + `DEMO_MODE=false` + rebuild |
| Docker Compose (demo/portfolio) | ✅ | Default config works with demo mode |
| Kubernetes | ❌ | No manifests; `k8s/` directory is empty |
| Cloud (AWS/GCP/Azure) | ❌ | No Terraform; no managed service configuration |
| CI/CD pipeline | ❌ | No workflow files exist |

---

## Recommended Steps to Reach Production

1. **Add CI/CD** — GitHub Actions workflow: lint → test → build → push image → deploy.
2. **Replace ThreadPoolExecutor** — Use Celery + Redis for reliable background job processing.
3. **Restrict CORS** — Change `allow_origins=["*"]` to the specific UI origin.
4. **Enable HTTPS** — Add a reverse proxy (nginx) with TLS certificates.
5. **Add alerting** — Configure Prometheus Alertmanager rules for error rate and job failure rate.
6. **Implement stuck-run TTL** — A cron job or scheduled task to fail runs stuck in RUNNING beyond N minutes.
7. **Non-root containers** — Add `USER 1000` to both Dockerfiles.
8. **Database backups** — Add `pg_dump` cron to Docker Compose or use managed PostgreSQL.
