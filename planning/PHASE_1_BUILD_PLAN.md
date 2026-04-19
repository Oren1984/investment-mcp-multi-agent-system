# 🚀 Phase 1 — Audit, Cleanup & Rebuild Plan
## Investment MCP Multi-Agent System

---

## 🎯 Goal of This Phase

Before building the system, perform a **full repository audit, cleanup, and structured rebuild plan**.

This phase is NOT about coding yet.

It is about:
- understanding what exists
- removing noise
- selecting the right components
- designing a clean architecture
- defining what will be built and why

At the end of this phase:
👉 A clear, structured build plan must be produced  
👉 No actual implementation should start yet  

---

## 🧠 Your Role

Act as:

- Senior AI Systems Engineer  
- Applied AI Engineer  
- MLOps Engineer  
- DevOps Architect  
- Backend Architect  
- QA Engineer  

Think production-level, not student-level.

---

## ⚠️ Critical Rule

❌ DO NOT start implementing the system  
❌ DO NOT write full production code yet  
❌ DO NOT build notebooks  
❌ DO NOT build static site  

✅ ONLY:
- analyze
- clean
- design
- plan

---

## 📦 Input Context

You are working on a repository based on an **AI System Templates Library**.

The following components may exist:

- shared-platform  
- agent-system-skeleton  
- rag-system-skeleton  
- ui-templates (Streamlit)  
- ds-ml-skeleton (optional, probably not needed)  
- dl-nlp-skeleton (optional, probably not needed)  

---

## 🧹 Step 1 — Full Repository Scan

Perform a deep scan of the repository:

### Identify:
- existing folders and files
- duplicated structures
- unused templates
- irrelevant components
- broken or partial structures
- missing critical layers

### Output:
Create a section:

## 🔍 Repository Audit

Include:
- what exists
- what is useful
- what is redundant
- what must be removed
- what is missing

---

## 🧼 Step 2 — Cleanup Plan

Define a **clear cleanup strategy**:

### Decide:
- which folders to keep
- which folders to delete
- which folders to merge
- which folders to restructure

### Output:
## 🧼 Cleanup Plan

Table format:

| Item | Action | Reason |
|------|--------|--------|
| folder/file | Keep / Remove / Refactor | explanation |

---

## 🧱 Step 3 — Final Architecture Design

Design the target architecture based on the project requirements:

### Required system layers:

- Streamlit UI
- FastAPI backend
- MCP Tool Gateway
- CrewAI orchestration
- Agents
- Services layer
- PostgreSQL
- Optional RAG (pgvector)
- Testing layer
- Infrastructure (Docker / K8s / Terraform)
- Monitoring (Prometheus / Grafana)

### Output:
## 🏗 Final Architecture

Include:
- layer breakdown
- responsibilities per layer
- data flow (step-by-step)
- boundaries between components

---

## 🤖 Step 4 — Agents Definition

Define the final agents:

Mandatory:
- Research Agent
- Technical Analyst
- Sector Analyst
- Risk Analyst
- Report Writer

Optional:
- Macro / News Analyst

### Output:
## 🤖 Agents Plan

For each agent:
- purpose
- inputs
- outputs
- dependencies (tools/services)

---

## 🛠 Step 5 — Tools & MCP Design

Define:

- tool registry structure
- input validation approach
- routing logic
- separation between tools and orchestration

### Output:
## 🛠 MCP & Tools Plan

Include:
- tool list
- responsibilities
- data contracts (inputs/outputs)

---

## 🗄 Step 6 — Database Design

Design PostgreSQL usage:

- tables
- relationships
- what is stored
- optional embeddings (pgvector)

### Output:
## 🗄 Database Plan

---

## 🧪 Step 7 — Testing Strategy

Define:

- unit tests scope
- integration tests scope
- smoke tests
- possible E2E approach

### Output:
## 🧪 Testing Plan

---

## ⚙️ Step 8 — DevOps & Infra Plan

Define:

- Docker structure
- docker-compose usage
- Kubernetes resources
- Terraform structure
- GCP readiness

### Output:
## ⚙️ Infrastructure Plan

---

## 📊 Step 9 — Monitoring Plan

Define:

- metrics exposure
- Prometheus usage
- Grafana dashboards
- logging strategy

### Output:
## 📊 Monitoring Plan

---

## 🖥 Step 10 — UI Plan

Define Streamlit UI:

- pages/components
- flow
- user actions
- outputs

### Output:
## 🖥 UI Plan

---

## 🚫 Explicit Non-Goals (For This Phase)

Do NOT include:
- notebooks
- static site
- presentation layer

These will be handled in Phase 3.

---

## 📋 Final Output Requirements

At the end, produce:

### 1. Full Structured Plan
Complete document covering all sections above.

### 2. Build Roadmap
Step-by-step execution plan:
1. backend
2. agents
3. UI
4. DB
5. tests
6. Docker
7. Kubernetes
8. Terraform
9. monitoring

### 3. Design Decisions Summary
Explain:
- why this architecture
- why these tools
- what was intentionally excluded

---

## ✅ Approval Gate

STOP after producing the plan.

Do NOT proceed to implementation.

Wait for explicit approval before moving to Phase 2 (build).