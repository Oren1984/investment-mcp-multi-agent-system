# 🧠 Investment MCP Multi-Agent System

Intelligent Financial Analysis • AI Agents • MLOps Architecture

---

## 📌 Overview

A production-oriented multi-agent AI system for stock analysis, built using:

- CrewAI orchestration
- MCP (Model Context Protocol) tool abstraction
- FastAPI backend
- Streamlit interface
- Observability stack (Prometheus + Grafana)

The system was designed as a real-world architecture, then adapted into a demo-ready version without external paid dependencies.

---

## 🎯 Purpose

This project demonstrates:

- Multi-agent system design
- AI orchestration patterns
- Backend engineering for AI systems
- MCP-based tool abstraction
- Production-to-demo adaptation strategy

---

## 🧠 System Design

Core Flow
User Request
    ↓
Streamlit UI
    ↓
FastAPI Backend
    ↓
CrewAI Orchestrator
    ↓
Specialized Agents
    ↓
MCP Tool Gateway
    ↓
Data Sources / Services
    ↓
Structured Report

---

## 🤖 Agents

Agent	            Responsibility
Research Agent	    Market data & fundamentals
Technical Agent	    Indicators & price analysis
Sector Agent	    Industry context
Risk Agent	        Risk evaluation
Report Agent	    Final structured output

---

##  ⚙️ Architecture

UI (Streamlit)
    → Backend (FastAPI)
        → CrewAI Orchestration
            → Agents Layer
                → MCP Gateway
                    → External/Internal Tools
                        → Database (PostgreSQL + pgvector)

---

## 📊 Monitoring

Prometheus → Grafana

---

## 📂 Project Structure

investment-mcp-multi-agent-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── crews/
│   │   ├── mcp/
│   │   ├── services/
│   │   ├── db/
│   │   ├── schemas/
│   │   └── core/
│   ├── tests/
│   └── requirements.txt
│
├── ui/
│   └── app/
│
├── infra/
│   ├── docker/
│   ├── k8s/
│   └── terraform/
│
├── monitoring/
├── docs/
├── notebooks/
├── static-site/
└── docker-compose.yml
---

## 🚀 Quick Start

```bash
cp .env.example .env
docker-compose up --build
```

Open:

UI → http://localhost:8501

API → http://localhost:8000/docs

---

## 🔌 API

Endpoint	                    Description
POST /api/v1/analyze	        Start analysis
GET /api/v1/analyze/{id}/status	Check status
GET /api/v1/analyze/{id}/report	Get result
GET /api/v1/health	            Health check
GET /api/v1/ready	            Readiness

---

##  🧪 Testing

```bash
pytest
```

Includes:

- Unit tests
- Integration tests
- E2E flows

---

## 📊 Observability

- Prometheus metrics
- Grafana dashboards
- Request lifecycle tracking
- Agent execution visibility

---

## 🔐 Security

- API Key authentication
- Rate limiting
- Report validation

---

## ⚠️ Known Limitations

- No RBAC (single API key)
- In-memory rate limiting
- External data reliability varies
- Demo mode may use mocked data

---

## 📚 Documentation

docs/
├── api_contracts.md
├── runbook.md
├── testing_matrix.md
├── qa_audit.md
├── known_limitations.md

---

## 🎤 Demo Assets

- Notebooks (demo + technical)
- Static portfolio site
- API walkthrough

---

## 🧩 Design Principles

- Structure-first engineering
- Modular architecture
- Separation of concerns
- API-first design
- Production-ready mindset

---

## 🧠 Key Highlights

- Multi-agent orchestration (CrewAI)
- MCP abstraction layer
- Async backend (FastAPI)
- Vector-ready DB (pgvector)
- Full Docker environment
- Kubernetes & Terraform ready

---

## 👨‍💻 Author

Oren Salami
AI Systems Engineer

---

## 🏁 Final Note

This project follows a production-first approach:

Build the full system →
Then adapt it into a clean, controlled demo →
Then present via static + notebooks.

---
