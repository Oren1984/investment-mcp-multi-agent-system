from crewai import Agent
from crewai.tools.base_tool import BaseTool as CrewAIBaseTool


def build_technical_analyst_agent(llm, tools: dict[str, CrewAIBaseTool]) -> Agent:
    return Agent(
        role="Technical Analysis Specialist",
        goal=(
            "Analyze price action and technical indicators to determine the current trend, "
            "momentum, key support/resistance levels, and short-to-medium term outlook."
        ),
        backstory=(
            "You are a chartered market technician (CMT) with expertise in price action, "
            "momentum indicators, and chart pattern analysis. You use data-driven signals "
            "rather than opinions and always interpret indicators in context of the broader trend. "
            "You express confidence levels and avoid overstating signals."
        ),
        tools=[tools["technical_indicators"], tools["stock_price"]],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=4,
    )
