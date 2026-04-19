#!/usr/bin/env bash
# smoke_docker.sh — Validates a running docker-compose stack end-to-end.
#
# Usage:
#   ./scripts/smoke_docker.sh [API_KEY]
#
# The optional API_KEY argument overrides the API_KEY environment variable.
# If neither is set, runs without auth (suitable when API_KEY is not configured).
#
# Assumes the stack is already up:  docker-compose up -d

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8010}"
API_KEY="${1:-${API_KEY:-}}"
TICKER="${SMOKE_TICKER:-MSFT}"
POLL_INTERVAL=10
POLL_MAX=60   # max polls before giving up (10s each → 10 min max)
READY_MAX=60  # seconds to wait for backend to become reachable

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}[INFO]${NC} $*"; }

auth_header() {
    if [[ -n "$API_KEY" ]]; then
        echo "-H" "X-API-Key: ${API_KEY}"
    else
        echo ""
    fi
}

# ── 0. Wait for backend to be reachable ───────────────────────────────────────
info "Waiting up to ${READY_MAX}s for backend at ${BASE_URL} ..."
for ((i=1; i<=READY_MAX; i++)); do
    if curl -sf "${BASE_URL}/api/v1/health" > /dev/null 2>&1; then
        pass "Backend reachable after ${i}s"
        break
    fi
    if [[ $i -eq $READY_MAX ]]; then
        fail "Backend did not become reachable within ${READY_MAX}s — is 'docker-compose up -d' done?"
    fi
    sleep 1
done

# ── 1. Health check ────────────────────────────────────────────────────────────
info "Checking /api/v1/health ..."
HEALTH=$(curl -sf "${BASE_URL}/api/v1/health") || fail "/health endpoint unreachable"
echo "$HEALTH" | grep -q '"status":"ok"' || fail "/health did not return status:ok — got: $HEALTH"
pass "/health → ok"

# ── 2. Readiness check ─────────────────────────────────────────────────────────
info "Checking /api/v1/ready ..."
READY=$(curl -sf "${BASE_URL}/api/v1/ready") || fail "/ready endpoint unreachable"
echo "$READY" | grep -q '"db":"ok"' || fail "DB not ready — got: $READY"
echo "$READY" | grep -q '"mcp_tools"' || fail "mcp_tools missing from /ready"
pass "/ready → db:ok, mcp_tools present"

# ── 3. Submit analysis ─────────────────────────────────────────────────────────
info "Submitting analysis for ${TICKER} ..."
SUBMIT=$(curl -sf -X POST "${BASE_URL}/api/v1/analyze" \
    -H "Content-Type: application/json" \
    $(auth_header) \
    -d "{\"ticker\": \"${TICKER}\", \"period\": \"1mo\"}") || fail "POST /analyze failed"

RUN_ID=$(echo "$SUBMIT" | grep -o '"run_id":"[^"]*"' | cut -d'"' -f4)
[[ -n "$RUN_ID" ]] || fail "No run_id in response: $SUBMIT"
pass "POST /analyze → run_id=${RUN_ID}"

# ── 4. Poll status until COMPLETED or FAILED ───────────────────────────────────
info "Polling status (max ${POLL_MAX} × ${POLL_INTERVAL}s) ..."
for ((i=1; i<=POLL_MAX; i++)); do
    STATUS_RESP=$(curl -sf "${BASE_URL}/api/v1/analyze/${RUN_ID}/status" $(auth_header)) || \
        fail "GET /status failed for run_id=${RUN_ID}"
    STATUS=$(echo "$STATUS_RESP" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    info "  [${i}/${POLL_MAX}] status=${STATUS}"

    if [[ "$STATUS" == "COMPLETED" ]]; then
        pass "Analysis completed (${i} polls)"
        break
    elif [[ "$STATUS" == "FAILED" ]]; then
        ERROR=$(echo "$STATUS_RESP" | grep -o '"error_message":"[^"]*"' | cut -d'"' -f4)
        fail "Analysis failed: ${ERROR}"
    fi

    if [[ $i -eq $POLL_MAX ]]; then
        fail "Analysis did not complete within $((POLL_MAX * POLL_INTERVAL))s"
    fi
    sleep "$POLL_INTERVAL"
done

# ── 5. Retrieve report ─────────────────────────────────────────────────────────
info "Retrieving report ..."
REPORT=$(curl -sf "${BASE_URL}/api/v1/analyze/${RUN_ID}/report" $(auth_header)) || \
    fail "GET /report failed for run_id=${RUN_ID}"
echo "$REPORT" | grep -qi "$TICKER" || fail "Ticker ${TICKER} not found in report content"
pass "Report retrieved — ticker ${TICKER} present in content"

# ── 6. History check ───────────────────────────────────────────────────────────
info "Checking history ..."
HISTORY=$(curl -sf "${BASE_URL}/api/v1/analyze?limit=5" $(auth_header)) || fail "GET /analyze failed"
echo "$HISTORY" | grep -q "$RUN_ID" || fail "Submitted run_id not found in history"
pass "History contains run_id=${RUN_ID}"

echo ""
echo -e "${GREEN}All smoke checks passed.${NC}"
