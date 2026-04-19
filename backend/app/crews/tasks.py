from crewai import Agent, Task


def build_research_task(agent: Agent, ticker: str, period: str) -> Task:
    return Task(
        description=(
            f"Conduct fundamental analysis of {ticker}. "
            f"Use the get_stock_price tool with ticker='{ticker}' and period='{period}' "
            f"and the get_financial_statements tool with ticker='{ticker}' statement_type='all'. "
            "Extract and summarize: revenue trend (YoY growth), earnings (EPS and trend), "
            "key valuation ratios (P/E, P/B, forward P/E), profit margins, debt levels, "
            "cash flow generation, and return on equity. "
            "Identify the top 3 financial strengths and top 3 financial concerns."
        ),
        expected_output=(
            "A structured fundamental analysis report section with: "
            "1. Company overview (1 paragraph), "
            "2. Financial highlights table (key metrics with values), "
            "3. Revenue and earnings trend analysis, "
            "4. Balance sheet assessment, "
            "5. Top 3 strengths and top 3 concerns. "
            "All numbers must be cited from tool data."
        ),
        agent=agent,
    )


def build_technical_task(agent: Agent, ticker: str) -> Task:
    return Task(
        description=(
            f"Perform technical analysis of {ticker}. "
            f"Use get_technical_indicators with ticker='{ticker}' period='6mo' "
            f"and get_stock_price with ticker='{ticker}' period='1y'. "
            "Analyze: current trend direction (using SMA 20/50/200 crossovers), "
            "momentum (RSI level and trend), MACD crossover signal, "
            "Bollinger Band position (is price extended?), volume confirmation, "
            "and identify key support/resistance levels from the price history. "
            "Provide an overall technical rating: STRONG_BUY / BUY / NEUTRAL / SELL / STRONG_SELL."
        ),
        expected_output=(
            "A technical analysis section with: "
            "1. Trend summary (1-2 sentences), "
            "2. Indicator readings table (RSI, MACD, SMA position, BB position), "
            "3. Key support and resistance levels, "
            "4. Volume analysis, "
            "5. Technical rating with justification. "
            "Be specific with indicator values from the tool output."
        ),
        agent=agent,
    )


def build_sector_task(agent: Agent, ticker: str) -> Task:
    return Task(
        description=(
            f"Conduct sector and competitive analysis for {ticker}. "
            f"Use get_sector_analysis with ticker='{ticker}'. "
            "Determine: which sector/industry the company belongs to, "
            "how its 1-year return compares to the sector ETF, "
            "relative valuation vs sector (P/E premium/discount), "
            "whether it is gaining or losing market share momentum, "
            "and key sector-level tailwinds and headwinds currently affecting the space."
        ),
        expected_output=(
            "A sector context section with: "
            "1. Sector classification and overview (2-3 sentences), "
            "2. Relative performance table (stock vs sector ETF), "
            "3. Valuation comparison vs sector, "
            "4. Competitive position assessment, "
            "5. Key sector tailwinds and headwinds. "
            "Include specific return figures and ETF name."
        ),
        agent=agent,
    )


def build_risk_task(agent: Agent, ticker: str) -> Task:
    return Task(
        description=(
            f"Analyze investment risks for {ticker}. "
            f"Use get_risk_metrics with ticker='{ticker}' period='1y' "
            f"and get_news_sentiment with ticker='{ticker}' days=14. "
            "Quantify: market risk (beta vs S&P 500), volatility (annualized), "
            "maximum historical drawdown, Sharpe ratio, daily VaR at 95% confidence, "
            "and recent news sentiment. "
            "Categorize overall risk level as: LOW / MODERATE / HIGH / VERY_HIGH "
            "based on all metrics combined."
        ),
        expected_output=(
            "A risk profile section with: "
            "1. Risk metrics table (beta, volatility, Sharpe, VaR, max drawdown), "
            "2. Risk interpretation (what each metric means in plain language), "
            "3. News sentiment summary (score, recent headlines), "
            "4. Overall risk rating (LOW/MODERATE/HIGH/VERY_HIGH) with rationale, "
            "5. Key risk factors (top 3). "
            "Cite all values from tool data."
        ),
        agent=agent,
    )


def build_report_task(agent: Agent, ticker: str, run_id: str) -> Task:
    return Task(
        description=(
            f"Write the final investment report for {ticker} by synthesizing all previous analyst outputs. "
            "Structure the report with these exact sections using markdown headers:\n"
            "# Investment Analysis Report: {ticker}\n"
            "## Executive Summary\n"
            "## Fundamental Analysis\n"
            "## Technical Analysis\n"
            "## Sector Context\n"
            "## Risk Profile\n"
            "## Investment Recommendation\n"
            "## Disclaimer\n\n"
            "The Recommendation section must include: "
            "BUY / HOLD / SELL rating, 12-month price target rationale, "
            "key catalysts to watch, and conditions that would change the view. "
            "After writing the report, save it using the save_report tool with "
            f"run_id='{run_id}', ticker='{ticker}', and the full report as content."
        ),
        expected_output=(
            "A complete, professional investment memo in markdown format covering all sections. "
            "The report is saved to the database via save_report tool. "
            "Return confirmation that the report was saved successfully."
        ),
        agent=agent,
        # context is set by InvestmentCrew after all tasks are created
    )
