from .agent import GPTResearcher
from .skills.diagnose_agent.writer import DiagnoseReportGenerator

from gpt_researcher.skills.diagnose_agent.researcher import DiagnoseResearchConductor
from .utils.enum import Tone, ReportType

class GPTDiagnoseResearcher(GPTResearcher):
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
        super(GPTDiagnoseResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: DiagnoseReportGenerator = DiagnoseReportGenerator(self)
        self.research_conductor: DiagnoseResearchConductor = DiagnoseResearchConductor(self)

    async def conduct_research(self, query=None):
        print("GPTDiagnoseResearcher conduct_research")
        await self.research_conductor.conduct_research(self.get_summary_query())

    async def write_summary_report(self) -> str:
        report = await self.report_generator.write_report(
            f'how {self.disorder} is diagnosed and confirmed',
            self.context
        )

        return report

    def get_summary_query(self):
        return f'how to diagnose {self.disorder}'
