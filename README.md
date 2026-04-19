# Oren Salami | 🧠 AI Systems Engineer

## Intelligent Systems • AI Agents • Data & Automation

---

## 🧠 AI System Templates Library

A clean, production-oriented collection of AI system skeletons.

This repository is a **structure-first AI engineering toolkit**.

It does NOT contain production implementations.  
It provides **reusable system skeletons** that are meant to be copied,
adapted, and extended inside real project repositories.

---

## 🎯 Purpose

Instead of starting from scratch, this library provides:

- Proven system structures
- Minimal but meaningful starter files
- Clear separation of concerns
- Consistent engineering patterns across projects

---

## 📦 Available Skeletons

| Skeleton | Purpose |
|--------|--------|
| DS/ML | Classic machine learning pipelines |
| DL/NLP | Deep learning & NLP workloads |
| RAG System | Retrieval-Augmented Generation systems |
| Agent System | Autonomous AI systems with tools |
| Shared Platform | Common infrastructure, integrations, security, observability, and runtime standards |
| UI Templates | Streamlit & React UI skeletons |

---

## 🧱 Project Structure

```text
ai-system-templates/
├── ds-ml-skeleton/
├── dl-nlp-skeleton/
├── rag-system-skeleton/
├── agent-system-skeleton/
├── shared-platform/
├── ui-templates/
│   ├── streamlit-ui-skeleton/
│   └── react-ui-skeleton/
├── examples/
│   └── rag_with_shared_platform/
├── prompts/
├── ai-system-templates-site/
├── .github/workflows/
│   └── ci.yml
└── .gitignore
```

> Each directory is self-contained and designed to be copied independently.

---

## 🧠 Philosophy

This library focuses on **structure, not implementation**.

You define:
- Architecture
- Flow
- Integration

You do NOT define here:
- Models
- Business-specific prompts
- Business logic

The `shared-platform` provides reusable infrastructure components such as:
configuration management, structured logging, security guards, timeout control,
retry logic, integration contracts, prompt templating, and observability foundations.

> **How to use this library:**  
> Copy the skeleton that fits your project type.  
> Combine it with `shared-platform` modules where needed.  
> Implement all business logic in a **separate downstream project repository**.  
> The skeleton stays clean — your project carries the implementation.

Each skeleton is intentionally minimal.  
It is designed to guide system structure — not to enforce implementation.

---

UI is a separate concern and is not embedded within system skeletons.  
It is handled as a dedicated layer with its own reusable structure.

UI templates are optional and can be swapped or replaced depending on project needs.

---

## 🎨 UI Layer

Frontend is not embedded in system skeletons.

Instead, use the dedicated UI templates:

- Streamlit → fast demos, internal tools, POCs
- React → production-ready frontend applications

This keeps backend, AI logic, and UI cleanly separated.

---

## 🚀 How to Use

1. Choose the relevant skeleton(s)
2. Copy them into a new project repository
3. Remove what is not needed
4. Add business logic and integrations
5. Adapt structure based on your system design
6. Run and evolve independently from this library

---

## 🔧 What’s Included

Each skeleton contains:

- `README.md`
- `.env.example`
- `requirements.txt`
- `Dockerfile`
- In shared-platform: optional reusable modules for config, logging, security, integrations, observability, retry, and timeout handling
- Optional: UI templates (Streamlit / React)
- Optional: `docker-compose.yml`, `tests/`, `ci/`

---

## 🚫 What’s NOT Included

- Model implementations
- Prompt engineering
- Pipelines
- Real datasets
- Business logic

---

## 🧠 Key Principle

> “I don’t just build AI models — I design and productionize AI systems.”

---

## 📌 When to Use What

- Use **DS/ML** → for classic ML tasks
- Use **DL/NLP** → for heavy models / GPU workloads
- Use **RAG** → when you need knowledge retrieval
- Use **Agent** → when actions & orchestration are required
- Use **Shared** → in every serious project that needs common standards, integrations, observability, security, or runtime controls
- Use **UI Templates** → when you need a ready-to-use frontend (Streamlit or React)

---

## ⚠️ Important

This repository is **not intended to be executed as-is**.

It is a **foundation layer** for building real systems in separate repositories.

---

## 🏁 Final Note

This is a **developer toolkit**, not a framework.

Use it to move fast, stay consistent, and build structured systems.

---

## License

This project is licensed under the MIT License.
See the `LICENSE` file for details.

---


