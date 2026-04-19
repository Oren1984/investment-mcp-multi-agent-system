# RAG Notebook Template

Use this structure for all exploration and experiment notebooks in this project.

---

## Naming convention

```
YYYY-MM-DD_topic-description.ipynb
```

Examples:
- `2025-01-15_chunking-strategy-comparison.ipynb`
- `2025-01-20_retrieval-top-k-evaluation.ipynb`
- `2025-02-01_reranking-model-comparison.ipynb`

---

## Standard notebook structure

```
# 1. Title and Goal
# 2. Setup & Imports
# 3. Configuration (load .env, set constants)
# 4. Data Loading
# 5. Experiment / Analysis
# 6. Results & Observations
# 7. Conclusions & Next Steps
```

---

## Recommended sections (template)

### 1. Title and Goal

**Purpose:** One sentence — what does this notebook explore?

**Date:** YYYY-MM-DD

**Author:** Name

---

### 2. Setup & Imports

```python
import os
from dotenv import load_dotenv
load_dotenv()

# Add shared-platform to path if running locally
import sys
sys.path.insert(0, "../../shared-platform")

from app_logging.logger import get_logger
logger = get_logger("notebook")
```

---

### 3. Configuration

```python
TOP_K = int(os.getenv("TOP_K", 5))
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
RERANK = os.getenv("RERANK_ENABLED", "true").lower() == "true"
```

---

### 4. Data Loading

```python
# Load raw documents or processed chunks
```

---

### 5. Experiment

```python
# Core experiment logic here
# Keep cells focused — one idea per cell group
```

---

### 6. Results

```python
# Visualize or summarize results
# Use tables or charts — not just print statements
```

---

### 7. Conclusions

```
- What worked
- What did not
- What to try next
- What to promote to src/
```

---

## Rules

- Notebooks are for exploration — **not production logic**
- Stable, reusable logic must be moved to `src/` or `rag/`
- Never commit outputs with secrets or personal data
- Keep notebooks reproducible — document environment and data sources
