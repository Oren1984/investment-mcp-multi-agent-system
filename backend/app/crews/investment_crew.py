from __future__ import annotations

from dataclasses import dataclass

from crewai import Crew, Process

from app.agents import (
    build_crewai_tools,
    build_report_writer_agent,
    build_research_agent,
    build_risk_analyst_agent,
    build_sector_analyst_agent,
    build_technical_analyst_agent,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.crews.tasks import (
    build_report_task,
    build_research_task,
    build_risk_task,
    build_sector_task,
    build_technical_task,
)
from app.db.models.analysis_run import RunStatus
from app.db.repositories.analysis_run_repo import AnalysisRunSyncRepository
from app.db.repositories.report_repo import ReportSyncRepository
from app.db.session import get_sync_session
from app.mcp.gateway import MCPGateway
from app.services.llm_service import LLMService, is_demo_mode
from app.services.report_service import ReportService

logger = get_logger(__name__)


@dataclass
class AnalysisConfig:
    ticker: str
    run_id: str
    period: str = "1y"


def _build_demo_report(ticker: str, period: str) -> str:
    """Return a clearly-labelled synthetic investment report for demo mode."""
    return f"""# Investment Analysis Report: {ticker}

> ⚠️ **DEMO MODE** — This report is synthetically generated. No real financial data was fetched
> and no LLM call was made. To enable live analysis, set a valid `ANTHROPIC_API_KEY` in `.env`
> and set `DEMO_MODE=false`.

---

## Executive Summary

**{ticker}** is used here as a demonstration ticker. This report illustrates the output format
and structure of the Investment MCP Multi-Agent System without requiring a live Anthropic API key.

In a real analysis run, this section would contain a concise 2–3 paragraph summary of the company,
its current market position, and the high-level investment thesis derived from the five-agent
analysis pipeline (Research → Technical → Sector → Risk → Report Writer).

**Analysis period:** {period}
**Mode:** Demo (synthetic)
**Agents run:** None (skipped in demo mode)

---

## Fundamental Analysis

In a live run, the Research Agent fetches financial statements via yfinance and produces:

- Revenue trend (YoY growth rate)
- EPS and earnings trajectory
- Key valuation ratios: P/E, forward P/E, P/B, EV/EBITDA
- Profit margins (gross, operating, net)
- Balance sheet health (debt/equity, current ratio)
- Cash flow generation (free cash flow yield)
- Return on equity and return on invested capital

**Demo placeholder values for {ticker}:**

| Metric | Demo Value |
|--------|-----------|
| Revenue Growth (YoY) | +12.4% |
| P/E Ratio | 28.3x |
| Gross Margin | 43.1% |
| Net Margin | 21.7% |
| Debt/Equity | 0.45 |
| Free Cash Flow Yield | 4.2% |

*These values are illustrative only. Run with a real API key to see actual data.*

---

## Technical Analysis

The Technical Analyst agent calculates RSI, MACD, Bollinger Bands, and SMA/EMA crossovers
from daily OHLCV data sourced via yfinance.

**Demo indicator readings for {ticker}:**

| Indicator | Demo Value | Signal |
|-----------|-----------|--------|
| RSI (14-period) | 54.2 | Neutral |
| MACD | +0.82 (above signal) | Bullish |
| SMA 20 vs SMA 50 | Price above both | Uptrend |
| Bollinger Band position | Mid-band | Neutral |
| Volume trend | In-line with avg | Neutral |

**Demo technical rating:** NEUTRAL — awaiting momentum confirmation.

*Real technical signals require a live backend connection and valid API key.*

---

## Sector Analysis

The Sector Analyst compares the ticker against its sector ETF using yfinance data.

**Demo sector context for {ticker}:**

- Sector: Technology (demo classification)
- Sector ETF benchmark: XLK (demo)
- 1-year relative performance: +3.2% vs sector (demo)
- Sector P/E premium/discount: trading at a slight premium to sector median

*Real sector data is fetched dynamically based on the ticker's yfinance sector classification.*

---

## Risk Assessment

The Risk Analyst calculates quantitative risk metrics from daily price returns.

**Demo risk metrics for {ticker}:**

| Metric | Demo Value | Interpretation |
|--------|-----------|----------------|
| Beta vs SPY | 1.18 | Slightly more volatile than market |
| Annualised Volatility | 26.3% | Moderate |
| Max Drawdown (period) | -14.7% | Manageable |
| Sharpe Ratio | 0.92 | Acceptable risk-adjusted return |
| VaR 95% (1-day) | -2.1% | On 95% of days, loss ≤ 2.1% |
| News Sentiment | +0.34 (Positive) | Moderately positive coverage |

**Demo risk rating:** MODERATE

*All values above are illustrative. Real metrics are calculated from actual OHLCV data.*

---

## Investment Recommendation

> ⚠️ **This recommendation is DEMO-GENERATED and has no basis in real analysis.**
> It exists solely to demonstrate the report output format.

**Demo Rating: HOLD**

**Rationale (demo):** Based on the illustrative metrics above, {ticker} presents a balanced
risk/reward profile with moderate technical momentum and reasonable fundamental valuation.
No real investment decision should be based on this demo output.

**Key catalysts to watch (demo):**
- Earnings reports and revenue guidance
- Sector rotation and macro environment
- Technical breakout above key resistance levels

**Conditions that would change the view (demo):**
- Deterioration in margin trends → would shift to SELL
- Strong earnings beat with raised guidance → would shift to BUY
- Market-wide risk-off → would shift to SELL

---

## Disclaimer

This report was generated by the Investment MCP Multi-Agent System in **DEMO MODE**.

All data, metrics, analysis, and recommendations in this report are **synthetically generated**
and do not reflect real financial data or analysis. This output is intended solely to demonstrate
the system's report structure and API flow.

**This is not financial advice.** Nothing in this report should be used to make investment
decisions. Always consult a qualified financial professional before making investment decisions.

To enable real AI-powered analysis: set `ANTHROPIC_API_KEY` to a valid key in `.env` and
restart the Docker stack with `DEMO_MODE=false`.
"""


class InvestmentCrew:
    def __init__(self, gateway: MCPGateway):
        self._gateway = gateway
        self._llm_service = LLMService()

    def run(self, config: AnalysisConfig) -> str:
        session = get_sync_session()
        run_repo = AnalysisRunSyncRepository(session)

        try:
            run_repo.update_status(config.run_id, RunStatus.RUNNING)
            logger.info("Crew started", extra={"run_id": config.run_id, "ticker": config.ticker})

            if is_demo_mode():
                logger.warning(
                    "Demo mode active — returning synthetic report without LLM call",
                    extra={"run_id": config.run_id, "ticker": config.ticker},
                )
                return self._run_demo(config, run_repo, session)

            return self._run_live(config, run_repo, session)

        except Exception as e:
            err_msg = str(e)
            # Detect Anthropic authentication errors specifically
            if "401" in err_msg or "authentication" in err_msg.lower() or "invalid x-api-key" in err_msg.lower():
                err_msg = (
                    "Anthropic API authentication failed (401). "
                    "The ANTHROPIC_API_KEY in .env is invalid or a placeholder. "
                    "Set a valid key and restart the backend, or set DEMO_MODE=true."
                )
                logger.error(
                    "Anthropic authentication failed — check ANTHROPIC_API_KEY in .env",
                    extra={"run_id": config.run_id},
                )
            else:
                logger.exception("Crew failed", extra={"run_id": config.run_id})
            run_repo.update_status(config.run_id, RunStatus.FAILED, error_message=err_msg)
            raise
        finally:
            session.close()

    def _run_demo(
        self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session
    ) -> str:
        import time
        time.sleep(0.5)  # brief pause to simulate async work

        content = _build_demo_report(config.ticker, config.period)

        report_svc = ReportService(session)
        structured = report_svc.parse_structured(content, config.ticker)
        structured["_demo_mode"] = True

        report_svc.save(
            run_id=config.run_id,
            ticker=config.ticker,
            content=content,
            structured=structured,
        )

        run_repo.update_status(config.run_id, RunStatus.COMPLETED)
        logger.info(
            "Demo report saved",
            extra={"run_id": config.run_id, "ticker": config.ticker},
        )
        return content

    def _run_live(
        self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session
    ) -> str:
        llm = self._llm_service.get_crewai_llm()
        tools = build_crewai_tools(self._gateway)

        research_agent = build_research_agent(llm, tools)
        technical_agent = build_technical_analyst_agent(llm, tools)
        sector_agent = build_sector_analyst_agent(llm, tools)
        risk_agent = build_risk_analyst_agent(llm, tools)
        report_agent = build_report_writer_agent(llm, tools)

        research_task = build_research_task(research_agent, config.ticker, config.period)
        technical_task = build_technical_task(technical_agent, config.ticker)
        sector_task = build_sector_task(sector_agent, config.ticker)
        risk_task = build_risk_task(risk_agent, config.ticker)
        report_task = build_report_task(report_agent, config.ticker, config.run_id)

        # Link context: report writer sees all previous outputs
        report_task.context = [research_task, technical_task, sector_task, risk_task]

        crew = Crew(
            agents=[research_agent, technical_agent, sector_agent, risk_agent, report_agent],
            tasks=[research_task, technical_task, sector_task, risk_task, report_task],
            process=Process.sequential,
            verbose=settings.crew_verbose,
        )

        result = crew.kickoff()
        final_output = str(result.raw) if hasattr(result, "raw") else str(result)

        # Persist per-agent task outputs
        if hasattr(result, "tasks_output"):
            agent_names = ["research", "technical_analyst", "sector_analyst", "risk_analyst", "report_writer"]
            for i, task_output in enumerate(result.tasks_output):
                name = agent_names[i] if i < len(agent_names) else f"agent_{i}"
                run_repo.save_agent_output(
                    run_id=config.run_id,
                    agent_name=name,
                    output_data={"output": str(task_output)},
                )

        logger.info("Crew completed", extra={"run_id": config.run_id})
        return final_output
