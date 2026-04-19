from crewai import Agent
from crewai.tools.base_tool import BaseTool as CrewAIBaseTool


def build_report_writer_agent(llm, tools: dict[str, CrewAIBaseTool]) -> Agent:
    return Agent(
        role="Investment Report Writer",
        goal=(
            "Synthesize all analyst findings into a clear, structured, professional investment report. "
            "The report must be actionable and follow a standard investment memo format."
        ),
        backstory=(
            "You are a senior investment writer who has authored hundreds of equity research reports "
            "for institutional clients. You excel at synthesizing complex data into clear narratives, "
            "identifying the key investment thesis, and presenting balanced views. "
            "Your reports are concise, well-structured, and always end with a concrete recommendation "
            "backed by the evidence presented. You never make up data — you only use what the analysts provide."
        ),
        tools=[tools["save_report"]],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
