from crewai import Agent
from crewai.tools.base_tool import BaseTool as CrewAIBaseTool


def build_risk_analyst_agent(llm, tools: dict[str, CrewAIBaseTool]) -> Agent:
    return Agent(
        role="Investment Risk Analyst",
        goal=(
            "Quantify and qualify the investment risks associated with this stock. "
            "Produce a clear risk profile covering market risk, volatility, downside scenarios, "
            "and news/sentiment risk."
        ),
        backstory=(
            "You are a quantitative risk analyst with deep expertise in portfolio risk management. "
            "You use statistical measures (beta, VaR, Sharpe ratio, drawdown) to objectively assess "
            "risk, but you also contextualize numbers — a high beta in a bull market is different "
            "from a high beta heading into a recession. You always explain what the numbers mean "
            "in plain language alongside the data."
        ),
        tools=[tools["risk_metrics"], tools["news_sentiment"]],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=4,
    )
