# 🚀 Phase 2 — Build Execution (Core System Only)

## Investment MCP Multi-Agent System

---

## 🎯 Goal of This Phase

Execute the full build of the **core system** based on the approved Phase 1 plan.

This phase is about:

* building the real system
* implementing architecture
* connecting all layers
* ensuring the system can run end-to-end

---

## ⚠️ Critical Scope Rules

### INCLUDED

* Backend (FastAPI)
* MCP Tool Gateway
* CrewAI agents
* Services layer
* Database integration (PostgreSQL)
* Streamlit UI
* Docker (Dockerfile + docker-compose)
* Kubernetes manifests (basic but correct)
* Terraform structure (GCP-ready, minimal but real)
* Monitoring base (metrics + Prometheus + Grafana structure)
* Logging (structured)

---

### EXCLUDED (DO NOT BUILD)

* ❌ Tests (unit / integration / e2e)
* ❌ Notebooks
* ❌ Static site
* ❌ Demo-only simplifications

---

## 🧠 Your Role

Act as:

* Senior AI Systems Engineer
* Backend Architect
* MLOps Engineer
* DevOps Engineer

Focus on:

* clean architecture
* real system flow
* maintainability
* production-oriented structure

---

## 🏗 Implementation Requirements

### 1. Backend — FastAPI

Build a clean FastAPI backend:

Must include:

* main app entry
* routes structure
* request/response schemas
* health endpoint
* readiness-style endpoint (optional but recommended)
* error handling
* config handling (.env based)

---

### 2. MCP Tool Gateway

Implement a proper MCP-like layer:

Must include:

* tool registry
* tool interface abstraction
* input validation
* routing logic
* separation from agents

Important:
Agents should NOT directly call services — they go through MCP.

---

### 3. Agents — CrewAI

Implement:

* Research Agent
* Technical Analyst
* Sector Analyst
* Risk Analyst
* Report Writer

Each agent must:

* have a clear role
* use relevant tools
* pass structured outputs
* not duplicate logic

Also implement:

* tasks
* crew builder
* execution flow

---

### 4. Services Layer

Implement clean services:

* market_data_service
* llm_service
* report_service
* risk_service
* optional rag_service (lightweight, no overkill)

Each service must:

* be reusable
* be testable (even if tests are not written yet)
* avoid direct coupling with UI or agents

---

### 5. Database — PostgreSQL

Implement:

* DB connection/session handling
* models
* repositories

Store:

* analyses
* runs
* reports
* agent outputs
* metadata

Optional:

* embeddings table (pgvector-ready, not overbuilt)

---

### 6. Streamlit UI

Build a clean UI:

Must include:

* ticker input
* run analysis button
* agent status/progress
* output sections
* chart display
* final report viewer
* download option (basic)

UI must:

* connect to FastAPI
* reflect real system state
* not fake behavior

---

### 7. Logging

Implement structured logging:

* JSON logs
* request_id or correlation_id
* clear log levels
* logs across backend/services

---

### 8. Monitoring

Implement base observability:

* metrics exposure endpoint (/metrics or equivalent)
* Prometheus config
* Grafana starter structure

Do NOT overbuild dashboards — keep it minimal but real.

---

### 9. Docker

Create:

* backend Dockerfile
* frontend Dockerfile
* docker-compose.yml

docker-compose must:

* run full system locally
* include DB
* wire services correctly

---

### 10. Kubernetes

Create minimal but correct manifests:

* deployment
* service
* config/secrets structure
* replicas
* load balancer (if relevant)

---

### 11. Terraform (GCP-ready)

Create:

* basic Terraform structure
* GKE cluster definition (simplified but realistic)
* node pool
* outputs

Do NOT overcomplicate.

---

## 🧱 Code Quality Rules

* no monolithic files
* clear separation of concerns
* meaningful naming
* no dead code
* no fake placeholder logic unless clearly marked
* avoid over-engineering

---

## 🔗 System Flow Requirement

The system must support:

UI → FastAPI → MCP → Agents → Services → DB → Report → UI

End-to-end flow must be logically complete.

---

## 📋 Documentation (Light Update Only)

Update only what is necessary:

* README.md
* .env.example

Do NOT create heavy docs in this phase.

---

## 📦 Expected Output

At the end, provide:

### 1. What Was Built

Clear summary of:

* components
* layers
* integrations

### 2. How to Run the System

* docker-compose instructions
* local run option (optional)

### 3. What Is Still Missing (By Design)

Explicitly mention:

* tests (phase 3)
* notebooks (phase 3)
* static site (phase 3)

---

## 🛑 Stop Condition

After completing implementation:

STOP.

Do NOT:

* add tests
* build notebooks
* create static site

Wait for next phase instructions.
