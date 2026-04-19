from crewai import Agent
from crewai.tools.base_tool import BaseTool as CrewAIBaseTool


def build_research_agent(llm, tools: dict[str, CrewAIBaseTool]) -> Agent:
    return Agent(
        role="Fundamental Research Analyst",
        goal=(
            "Gather and analyze fundamental financial data for a given stock ticker. "
            "Provide a comprehensive assessment of the company's financial health, "
            "growth trajectory, and valuation."
        ),
        backstory=(
            "You are a seasoned fundamental analyst with 15 years of experience at top investment banks. "
            "You specialize in reading financial statements, identifying key growth drivers, "
            "and spotting red flags in company financials. You are rigorous, fact-based, "
            "and always cite specific numbers when making claims."
        ),
        tools=[tools["stock_price"], tools["financial_statements"]],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
