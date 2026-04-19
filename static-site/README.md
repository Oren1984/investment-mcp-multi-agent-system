# Investment MCP Multi-Agent System — Static Demo Site

## What This Is

A standalone, self-contained portfolio/demo page for the Investment MCP Multi-Agent System.
It is a pure HTML/CSS/JS site — no build step, no server required to view.

It showcases the system's architecture, agents, testing strategy, and deployment design through
an interactive static presentation. The "Run Analysis" button in the Live Demo section simulates
the log stream and output of a real analysis run without connecting to any backend.

## What It Demonstrates

- System overview and problem statement
- Full architecture diagram (layer-by-layer)
- The 5 specialized AI agents and their MCP tools
- Simulated analysis log stream (interactive, no backend needed)
- Testing strategy across Unit / Integration / Smoke / E2E layers
- Jupyter notebook descriptions
- Deployment options: Docker Compose, Kubernetes, Terraform/GCP

## Folder Structure

```
static-site/
├── index.html   — Main page (all sections)
├── style.css    — Dark-themed responsive styles (Inter + JetBrains Mono fonts)
├── script.js    — Canvas animations, tab switching, demo simulation, counters
└── README.md    — This file
```

## How to Open Locally

### Option A — Open Directly (simplest)

Double-click `index.html` in File Explorer, or drag it into a browser.

This works for viewing content but some browsers restrict local `fetch()` calls.
For full interactivity (the demo simulation is pure JS — no fetch), this is fine.

### Option B — Python HTTP Server (recommended)

```powershell
# Navigate to the static-site folder
cd C:\Users\ORENS\investment-mcp-multi-agent-system\static-site

# Python 3
python -m http.server 8080
```

Then open: http://localhost:8080

### Option C — PowerShell One-Liner

```powershell
cd C:\Users\ORENS\investment-mcp-multi-agent-system\static-site
python -m http.server 8080; Start-Process "http://localhost:8080"
```

### Option D — Node.js (if installed)

```powershell
cd C:\Users\ORENS\investment-mcp-multi-agent-system\static-site
npx serve .
```

## What Is Static vs What Requires a Backend

| Feature | Static (works offline) | Requires backend |
|---------|------------------------|------------------|
| Architecture diagrams | ✅ | — |
| Agent descriptions | ✅ | — |
| Deployment documentation | ✅ | — |
| Testing strategy tabs | ✅ | — |
| Hero particle animation | ✅ | — |
| Animated metric counters | ✅ | — |
| "Run Analysis" simulation | ✅ simulated log stream | — |
| Real analysis run | — | ✅ docker-compose stack |
| Actual report output | — | ✅ + ANTHROPIC_API_KEY |

The "Run Analysis" button runs a JavaScript simulation that replays a realistic log stream
for any selected ticker. No network call is made. The output is pre-scripted and
is not connected to the real CrewAI analysis pipeline.

## How It Relates to the Real System

The static site documents and demonstrates the same system that is running in the Docker stack:

```
static-site/index.html     ← portfolio/demo page (this)
backend/                   ← FastAPI + CrewAI (docker-compose backend service)
ui/                        ← Streamlit UI (docker-compose ui service, port 8501)
```

To run the **real** analysis pipeline:

```bash
# 1. Copy and fill in environment variables
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY, DATABASE_URL, etc.

# 2. Start the full stack
docker-compose up --build

# 3. Open the Streamlit UI
# http://localhost:8501

# 4. Or use the API directly
# http://localhost:8010/docs
```

## Limitations of the Static Demo

- The "Run Analysis" simulation does not call the real API — outputs are scripted
- No real financial data is fetched in the static demo
- Report content shown is illustrative, not AI-generated
- The GitHub Repository link in the hero section points to `https://github.com` (placeholder — update to the real repo URL)

## Troubleshooting

**Fonts not loading (Inter / JetBrains Mono):**
The site loads fonts from Google Fonts over the internet. If you are offline, the browser
will fall back to system fonts. The layout is unaffected.

**Canvas animation not showing:**
Requires a browser with Canvas API support (all modern browsers). If blank, check the
browser console for errors.

**Tabs not switching:**
JavaScript must be enabled. The `script.js` file must load — verify no 404 in the
browser network tab.

**Styles look broken when opening as file://**
Some browsers (Chrome) restrict certain CSS features on file:// URLs. Use the Python
HTTP server approach (Option B above) for best results.
