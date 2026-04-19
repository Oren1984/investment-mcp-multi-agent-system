from crewai import Agent
from crewai.tools.base_tool import BaseTool as CrewAIBaseTool


def build_sector_analyst_agent(llm, tools: dict[str, CrewAIBaseTool]) -> Agent:
    return Agent(
        role="Sector & Competitive Intelligence Analyst",
        goal=(
            "Place the stock in its sector and competitive context. "
            "Assess its relative valuation, sector performance, and competitive positioning."
        ),
        backstory=(
            "You are an industry specialist who has covered multiple sectors for a decade. "
            "You understand sector cycles, competitive dynamics, and how macro trends affect "
            "individual stocks. You compare companies to their sector benchmarks rigorously "
            "and provide context that fundamental or technical analysis alone cannot capture."
        ),
        tools=[tools["sector_analysis"], tools["stock_price"]],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=4,
    )
