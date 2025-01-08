from .agent import GPTResearcher
from .skills.therapy_agent.writer import TherapyReportGenerator

from gpt_researcher.skills.disorder_agent import DisorderResearchConductor
from .utils.enum import Tone, ReportType

class GPTTherapyResearcher(GPTResearcher):
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
        super(GPTTherapyResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: TherapyReportGenerator = TherapyReportGenerator(self)
        self.research_conductor: DisorderResearchConductor = DisorderResearchConductor(self)

    async def conduct_context_research(self, query):
        print("GPTMedResearcher conduct_research")
        await self.research_conductor.generate_global_context(query)

    async def get_therapy_list(self):
        return await self.report_generator.get_therapy_list(f'therapies for {self.disorder}')

    async def write_general_therapy_report(self, query) -> str:
        report = await self.report_generator.write_report(
            query,
            self.context
        )

        return report

