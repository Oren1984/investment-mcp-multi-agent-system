from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

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
    execution_mode: str = "hybrid"  # rag_only | agent_only | hybrid


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def _build_demo_report(ticker: str, period: str, execution_mode: str = "hybrid") -> str:
    mode_label = {
        "rag_only": "RAG Only (Demo Data Snapshot)",
        "agent_only": "Agent Only (Synthetic Report)",
        "hybrid": "Hybrid — RAG + Agent (Synthetic Report)",
    }.get(execution_mode, "Demo")

    return f"""# Investment Analysis Report: {ticker}

> ⚠️ **DEMO MODE** — This report is synthetically generated. No real financial data was fetched
> and no LLM call was made. To enable live analysis, set a valid `ANTHROPIC_API_KEY` in `.env`
> and set `DEMO_MODE=false`.

**Execution Mode:** {mode_label}

---

## Executive Summary

**{ticker}** is used here as a demonstration ticker. This report illustrates the output format
and structure of the Investment MCP Multi-Agent System without requiring a live Anthropic API key.

In a real analysis run, this section would contain a concise 2–3 paragraph summary of the company,
its current market position, and the high-level investment thesis derived from the five-agent
analysis pipeline (Research → Technical → Sector → Risk → Report Writer).

**Analysis period:** {period}
**Mode:** Demo (synthetic) — {mode_label}
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


def _build_rag_snapshot_report(ticker: str, period: str, rag_result: dict, elapsed_s: float) -> str:
    """Format raw MCP tool data as a structured Market Data Snapshot report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    data = rag_result.get("data", {})
    errors = rag_result.get("errors", {})
    sources_used = rag_result.get("sources_used", [])
    sources_failed = rag_result.get("sources_failed", [])

    lines = [
        f"# Market Data Snapshot: {ticker}",
        "",
        "> **Execution Mode: RAG Only** — Raw data retrieved from sources without LLM synthesis.",
        "> This snapshot shows market intelligence collected directly by the MCP tool layer.",
        "",
        f"**Ticker:** {ticker} | **Period:** {period} | **Retrieved:** {timestamp} | **Elapsed:** {elapsed_s:.2f}s",
        "",
        "---",
        "",
    ]

    # Price section
    price_data = data.get("stock_price", {})
    if price_data:
        current_price = price_data.get("current_price")
        price_change = price_data.get("price_change_pct")
        hist = price_data.get("data", {})
        n_days = len(hist)
        lines += [
            "## Price Overview",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Current Price | ${current_price:.2f} |" if current_price else "| Current Price | N/A |",
            f"| Period Return ({period}) | {price_change:+.2f}% |" if price_change is not None else "| Period Return | N/A |",
            f"| Trading Days in History | {n_days} |",
            f"| Source | Yahoo Finance |",
            "",
        ]
    else:
        lines += ["## Price Overview", "", "_Price data unavailable._", ""]

    # Financial Highlights
    fin_data = data.get("financial_statements", {})
    if fin_data:
        metrics = fin_data.get("key_metrics", {})
        income = fin_data.get("income_statement", {})

        lines += ["## Financial Highlights", ""]
        if metrics:
            lines += ["| Metric | Value |", "|--------|-------|"]
            for k, v in list(metrics.items())[:12]:
                if v is not None:
                    formatted = f"{v:.2f}" if isinstance(v, float) else str(v)
                    lines.append(f"| {k.replace('_', ' ').title()} | {formatted} |")
            lines += ["", f"_Source: Yahoo Finance_", ""]
        else:
            lines += ["_Financial metrics not available._", ""]
    else:
        err = errors.get("financial_statements", "")
        lines += ["## Financial Highlights", "", f"_Data unavailable: {err}_" if err else "_Data unavailable._", ""]

    # Technical Indicators
    tech_data = data.get("technical_indicators", {})
    if tech_data:
        lines += [
            "## Technical Indicators",
            "",
            "| Indicator | Value | Signal |",
            "|-----------|-------|--------|",
        ]
        rsi = tech_data.get("rsi_14")
        macd = tech_data.get("macd")
        macd_signal = tech_data.get("macd_signal")
        trend = tech_data.get("trend", "N/A")
        rsi_signal = tech_data.get("rsi_signal", "N/A")
        sma20 = tech_data.get("sma_20")
        sma50 = tech_data.get("sma_50")
        bb_upper = tech_data.get("bollinger_upper")
        bb_lower = tech_data.get("bollinger_lower")

        if rsi is not None:
            lines.append(f"| RSI (14-period) | {rsi:.1f} | {rsi_signal} |")
        if macd is not None and macd_signal is not None:
            lines.append(f"| MACD | {macd:.3f} | {'Above signal' if macd > macd_signal else 'Below signal'} |")
        if sma20 is not None:
            lines.append(f"| SMA 20 | {sma20:.2f} | — |")
        if sma50 is not None:
            lines.append(f"| SMA 50 | {sma50:.2f} | — |")
        lines += [f"| Overall Trend | — | {trend} |", "", f"_Source: Yahoo Finance + Calculated_", ""]
    else:
        err = errors.get("technical_indicators", "")
        lines += ["## Technical Indicators", "", f"_Data unavailable: {err}_" if err else "_Data unavailable._", ""]

    # Sector Context
    sector_data = data.get("sector_analysis", {})
    if sector_data:
        sector = sector_data.get("sector", "N/A")
        etf = sector_data.get("sector_etf", "N/A")
        stock_ret = sector_data.get("stock_1y_return_pct")
        etf_ret = sector_data.get("sector_1y_return_pct")
        rel_perf = sector_data.get("relative_performance_pct")
        lines += [
            "## Sector Context",
            "",
            f"**Sector:** {sector} | **Benchmark ETF:** {etf}",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Stock 1Y Return | {stock_ret:+.2f}% |" if stock_ret is not None else "| Stock 1Y Return | N/A |",
            f"| Sector ETF 1Y Return | {etf_ret:+.2f}% |" if etf_ret is not None else "| Sector ETF 1Y Return | N/A |",
            f"| Relative Performance | {rel_perf:+.2f}% |" if rel_perf is not None else "| Relative Performance | N/A |",
            "",
            f"_Source: Yahoo Finance_",
            "",
        ]
    else:
        err = errors.get("sector_analysis", "")
        lines += ["## Sector Context", "", f"_Data unavailable: {err}_" if err else "_Data unavailable._", ""]

    # Risk Metrics
    risk_data = data.get("risk_metrics", {})
    if risk_data:
        lines += [
            "## Risk Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ]
        field_map = [
            ("beta", "Beta vs SPY"),
            ("annualized_volatility_pct", "Annualised Volatility (%)"),
            ("max_drawdown_pct", "Max Drawdown (%)"),
            ("sharpe_ratio", "Sharpe Ratio"),
            ("var_95_1day_pct", "VaR 95% (1-day, %)"),
            ("annualized_return_pct", "Annualised Return (%)"),
        ]
        for key, label in field_map:
            val = risk_data.get(key)
            if val is not None:
                lines.append(f"| {label} | {val:.2f} |")
        lines += ["", "_Source: Yahoo Finance + Calculated_", ""]
    else:
        err = errors.get("risk_metrics", "")
        lines += ["## Risk Metrics", "", f"_Data unavailable: {err}_" if err else "_Data unavailable._", ""]

    # News Sentiment
    news_data = data.get("news_sentiment", {})
    if news_data:
        score = news_data.get("sentiment_score", 0.0)
        label = news_data.get("sentiment_label", "N/A")
        article_count = news_data.get("article_count", 0)
        headlines = news_data.get("headlines", [])
        src = news_data.get("_source", "newsapi")
        lines += [
            "## News Sentiment",
            "",
            f"**Score:** {score:+.2f} | **Label:** {label} | **Articles:** {article_count} | **Source:** {src.replace('_', ' ').title()}",
            "",
        ]
        if headlines:
            lines += ["**Recent headlines:**", ""]
            for h in headlines[:5]:
                lines.append(f"- {h}")
            lines.append("")
    else:
        lines += ["## News Sentiment", "", "_Sentiment data unavailable._", ""]

    # Provenance
    lines += [
        "---",
        "",
        "## Data Provenance",
        "",
        "| Data Type | Source | Status |",
        "|-----------|--------|--------|",
    ]
    provenance = [
        ("Price History", "Yahoo Finance", "stock_price"),
        ("Financial Statements", "Yahoo Finance", "financial_statements"),
        ("Technical Indicators", "Yahoo Finance + Calculated", "technical_indicators"),
        ("Sector Comparison", "Yahoo Finance", "sector_analysis"),
        ("Risk Metrics", "Yahoo Finance + Calculated", "risk_metrics"),
        ("News Sentiment", "News API / Keyword Fallback", "news_sentiment"),
    ]
    for label, source, key in provenance:
        status = "OK" if key in sources_used else f"FAILED — {errors.get(key, 'error')}"
        lines.append(f"| {label} | {source} | {status} |")

    lines += [
        "",
        "---",
        "",
        "*This is a raw data retrieval result (RAG Only mode). "
        "For AI-synthesized investment analysis, use **Agent Only** or **Hybrid** mode.*",
        "",
        "**This is not financial advice.**",
    ]

    return "\n".join(lines)


def _format_rag_context_summary(rag_result: dict) -> str:
    """Compact text summary of pre-fetched RAG data, for injection into hybrid agent context."""
    data = rag_result.get("data", {})
    ticker = rag_result.get("ticker", "")
    lines = [f"[Pre-fetched raw data for {ticker}]"]

    price = data.get("stock_price", {})
    if price:
        cp = price.get("current_price")
        pch = price.get("price_change_pct")
        lines.append(f"Price: ${cp:.2f}, {rag_result.get('period', '1y')} return: {pch:+.2f}%"
                     if cp and pch is not None else "Price: N/A")

    risk = data.get("risk_metrics", {})
    if risk:
        lines.append(
            f"Risk: beta={risk.get('beta', 'N/A')}, "
            f"vol={risk.get('annualized_volatility_pct', 'N/A')}%, "
            f"sharpe={risk.get('sharpe_ratio', 'N/A')}, "
            f"maxdd={risk.get('max_drawdown_pct', 'N/A')}%"
        )

    tech = data.get("technical_indicators", {})
    if tech:
        lines.append(
            f"Technicals: RSI={tech.get('rsi', 'N/A')}, "
            f"trend={tech.get('trend_signal', 'N/A')}, "
            f"RSI signal={tech.get('rsi_signal', 'N/A')}"
        )

    sector = data.get("sector_analysis", {})
    if sector:
        lines.append(
            f"Sector: {sector.get('sector', 'N/A')}, ETF={sector.get('sector_etf', 'N/A')}, "
            f"relative perf={sector.get('relative_performance_pct', 'N/A')}%"
        )

    news = data.get("news_sentiment", {})
    if news:
        lines.append(
            f"News: score={news.get('sentiment_score', 'N/A')}, "
            f"label={news.get('sentiment_label', 'N/A')}"
        )

    failed = rag_result.get("sources_failed", [])
    if failed:
        lines.append(f"Failed tools: {', '.join(failed)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# InvestmentCrew
# ---------------------------------------------------------------------------

class InvestmentCrew:
    def __init__(self, gateway: MCPGateway):
        self._gateway = gateway
        self._llm_service = LLMService()

    def run(self, config: AnalysisConfig) -> str:
        session = get_sync_session()
        run_repo = AnalysisRunSyncRepository(session)

        try:
            run_repo.update_status(config.run_id, RunStatus.RUNNING)
            logger.info(
                "Crew started",
                extra={"run_id": config.run_id, "ticker": config.ticker, "mode": config.execution_mode},
            )

            # RAG Only never needs LLM — attempt real data fetch even in demo mode
            if config.execution_mode == "rag_only":
                if is_demo_mode():
                    return self._run_demo(config, run_repo, session)
                return self._run_rag_only(config, run_repo, session)

            # Agent Only and Hybrid require LLM
            if is_demo_mode():
                logger.warning(
                    "Demo mode active — returning synthetic report without LLM call",
                    extra={"run_id": config.run_id, "mode": config.execution_mode},
                )
                return self._run_demo(config, run_repo, session)

            if config.execution_mode == "hybrid":
                return self._run_hybrid(config, run_repo, session)

            return self._run_live(config, run_repo, session)

        except Exception as e:
            err_msg = str(e)
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

    def _run_demo(self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session) -> str:
        import time
        time.sleep(0.5)

        content = _build_demo_report(config.ticker, config.period, config.execution_mode)

        report_svc = ReportService(session)
        structured = report_svc.parse_structured(content, config.ticker)
        structured["_demo_mode"] = True
        structured["_execution_mode"] = config.execution_mode

        report_svc.save(
            run_id=config.run_id,
            ticker=config.ticker,
            content=content,
            structured=structured,
        )
        run_repo.update_status(config.run_id, RunStatus.COMPLETED)
        logger.info("Demo report saved", extra={"run_id": config.run_id, "ticker": config.ticker})
        return content

    def _run_rag_only(self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session) -> str:
        import time
        t0 = time.perf_counter()
        logger.info("RAG-only pass started", extra={"run_id": config.run_id, "ticker": config.ticker})

        rag_result = self._gateway.execute_rag_pass(config.ticker, config.period)
        elapsed = round(time.perf_counter() - t0, 2)

        content = _build_rag_snapshot_report(config.ticker, config.period, rag_result, elapsed)

        report_svc = ReportService(session)
        structured = report_svc.parse_structured(content, config.ticker)
        structured["_execution_mode"] = "rag_only"
        structured["_sources_used"] = rag_result.get("sources_used", [])
        structured["_sources_failed"] = rag_result.get("sources_failed", [])
        structured["_elapsed_s"] = elapsed

        report_svc.save(
            run_id=config.run_id,
            ticker=config.ticker,
            content=content,
            structured=structured,
        )
        run_repo.update_status(config.run_id, RunStatus.COMPLETED)
        logger.info("RAG-only report saved", extra={"run_id": config.run_id, "elapsed_s": elapsed})
        return content

    def _run_live(self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session) -> str:
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

        report_task.context = [research_task, technical_task, sector_task, risk_task]

        crew = Crew(
            agents=[research_agent, technical_agent, sector_agent, risk_agent, report_agent],
            tasks=[research_task, technical_task, sector_task, risk_task, report_task],
            process=Process.sequential,
            verbose=settings.crew_verbose,
        )

        result = crew.kickoff()
        final_output = str(result.raw) if hasattr(result, "raw") else str(result)

        if hasattr(result, "tasks_output"):
            agent_names = [
                "research", "technical_analyst", "sector_analyst", "risk_analyst", "report_writer"
            ]
            for i, task_output in enumerate(result.tasks_output):
                name = agent_names[i] if i < len(agent_names) else f"agent_{i}"
                run_repo.save_agent_output(
                    run_id=config.run_id,
                    agent_name=name,
                    output_data={"output": str(task_output)},
                )

        logger.info("Crew completed (agent_only)", extra={"run_id": config.run_id})
        return final_output

    def _run_hybrid(self, config: AnalysisConfig, run_repo: AnalysisRunSyncRepository, session) -> str:
        import time
        logger.info("Hybrid mode: starting RAG pre-fetch", extra={"run_id": config.run_id})

        t0 = time.perf_counter()
        rag_result = self._gateway.execute_rag_pass(config.ticker, config.period)
        rag_elapsed = round(time.perf_counter() - t0, 2)
        rag_context = _format_rag_context_summary(rag_result)

        logger.info(
            "Hybrid mode: RAG pre-fetch complete — starting agents",
            extra={"run_id": config.run_id, "rag_elapsed_s": rag_elapsed, "sources": rag_result.get("sources_used")},
        )

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
        report_task = build_report_task(
            report_agent, config.ticker, config.run_id, rag_context=rag_context
        )

        report_task.context = [research_task, technical_task, sector_task, risk_task]

        crew = Crew(
            agents=[research_agent, technical_agent, sector_agent, risk_agent, report_agent],
            tasks=[research_task, technical_task, sector_task, risk_task, report_task],
            process=Process.sequential,
            verbose=settings.crew_verbose,
        )

        result = crew.kickoff()
        final_output = str(result.raw) if hasattr(result, "raw") else str(result)

        if hasattr(result, "tasks_output"):
            agent_names = [
                "research", "technical_analyst", "sector_analyst", "risk_analyst", "report_writer"
            ]
            for i, task_output in enumerate(result.tasks_output):
                name = agent_names[i] if i < len(agent_names) else f"agent_{i}"
                run_repo.save_agent_output(
                    run_id=config.run_id,
                    agent_name=name,
                    output_data={
                        "output": str(task_output),
                        "_rag_pre_fetched": True,
                    },
                )

        logger.info("Crew completed (hybrid)", extra={"run_id": config.run_id})
        return final_output
