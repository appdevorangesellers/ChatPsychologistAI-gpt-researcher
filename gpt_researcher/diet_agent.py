from .agent import GPTResearcher
from .skills.diet_agent.writer import DietReportGenerator

from gpt_researcher.skills.diet_agent.researcher import DietResearchConductor
from .utils.enum import Tone, ReportType

class GPTDietResearcher(GPTResearcher):
    def __init__(
        self,
        disorder: str = "",
        report_type: str = ReportType.ResearchReport.value,
        tone: Tone = Tone.Objective,
        config_path="default",
        subtopics: list = [],
        websocket=None,
        verbose: bool = True
    ):
        super(GPTDietResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: DietReportGenerator = DietReportGenerator(self)
        self.research_conductor: DietResearchConductor = DietResearchConductor(self)

    async def conduct_research(self, query=None):
        print("GPTSymptomResearcher conduct_research")
        await self.research_conductor.conduct_research(self.get_summary_query())

    async def write_summary_report(self) -> str:
        report = await self.report_generator.write_report(
            self.get_summary_query(),
            self.context
        )

        return report

    def get_summary_query(self):
        return f'diets related to {self.disorder}'
