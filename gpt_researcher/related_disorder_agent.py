from .agent import GPTResearcher
from .skills.related_disorder_agent.writer import RelatedDisorderReportGenerator

from gpt_researcher.skills.disorder_agent import DisorderResearchConductor
from .utils.enum import Tone, ReportType

class GPTRelatedDisorderResearcher(GPTResearcher):
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
        super(GPTRelatedDisorderResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: RelatedDisorderReportGenerator = RelatedDisorderReportGenerator(self)
        self.research_conductor: DisorderResearchConductor = DisorderResearchConductor(self)

    async def conduct_research(self, query=None):
        print("GPTDiagnoseResearcher conduct_research")
        await self.research_conductor.conduct_research(self.get_summary_query())

    async def write_summary_report(self) -> str:
        report = await self.report_generator.write_report(
            self.get_summary_query(),
            self.context
        )

        return report

    def get_summary_query(self):
        return f'disorders related to {self.disorder}'
