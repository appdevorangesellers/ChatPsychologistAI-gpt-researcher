from .agent import GPTResearcher
from .skills.symptom_agent.writer import SymptomReportGenerator

from gpt_researcher.skills.symptom_agent.researcher import SymptomResearchConductor
from .utils.enum import Tone, ReportType

class GPTSymptomResearcher(GPTResearcher):
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
        super(GPTSymptomResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: SymptomReportGenerator = SymptomReportGenerator(self)
        self.research_conductor: SymptomResearchConductor = SymptomResearchConductor(self)

    '''async def conduct_research(self, query=None):
        print("GPTSymptomResearcher conduct_research")
        await self.research_conductor.conduct_research(self.disorder)'''

    async def write_summary_report(self) -> str:
        report = await self.report_generator.write_report(
            f'symptoms related to {self.disorder}',
            self.context
        )

        return report
