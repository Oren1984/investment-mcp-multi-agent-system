# Agent System Notebook Template

Use this structure for all exploration and experiment notebooks in this project.

---

## Naming convention

```
YYYY-MM-DD_topic-description.ipynb
```

Examples:
- `2025-01-15_tool-call-latency-benchmark.ipynb`
- `2025-01-20_memory-retrieval-quality.ipynb`
- `2025-02-01_planner-strategy-comparison.ipynb`

---

## Standard notebook structure

```
# 1. Title and Goal
# 2. Setup & Imports
# 3. Configuration
# 4. Agent / Tool Setup
# 5. Experiment Run
# 6. Results & Observations
# 7. Conclusions & Next Steps
```

---

## Recommended sections (template)

### 1. Title and Goal

**Purpose:** One sentence — what agent behavior does this notebook explore?

**Date:** YYYY-MM-DD

**Author:** Name

---

### 2. Setup & Imports

```python
import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, "../../shared-platform")

from app_logging.logger import get_logger
from resilience.retry import retry
logger = get_logger("notebook")
```

---

### 3. Configuration

```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
APPROVALS_ENABLED = os.getenv("APPROVALS_ENABLED", "true").lower() == "true"
```

---

### 4. Agent / Tool Setup

```python
# Initialize agent components
# Load tools
# Configure memory boundaries
```

---

### 5. Experiment Run

```python
# Define input scenario
# Run agent step-by-step or full execution
# Capture intermediate outputs for analysis
```

---

### 6. Results

```python
# Analyze tool call patterns
# Measure latency, token usage, approval triggers
# Compare against baseline or alternative approach
```

---

### 7. Conclusions

```
- What the agent did well
- Where it failed or required correction
- What prompt / tool / memory change to try next
- What to promote to agents/ or orchestration/
```

---

## Rules

- Notebooks are for exploration — **not production logic**
- Working agent logic belongs in `agents/`, `tools/`, or `orchestration/`
- Never commit real API keys or sensitive outputs
- Document which model and tool configuration was active during the experiment
