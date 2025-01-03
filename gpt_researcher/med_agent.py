from .agent import GPTResearcher
from .skills.med_agent.writer import MedReportGenerator

from gpt_researcher.skills.med_agent.researcher import MedResearchConductor
from .utils.enum import Tone, ReportType

class GPTMedResearcher(GPTResearcher):
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
        super(GPTMedResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.disorder = disorder
        self.report_generator: MedReportGenerator = MedReportGenerator(self)
        self.med_research_conductor: MedResearchConductor = MedResearchConductor(self)

    async def conduct_context_research(self, query):
        print("GPTMedResearcher conduct_research")
        # self.context = await self.research_conductor.conduct_research()
        await self.med_research_conductor.generate_global_context(query)
        # subprocess.run(['graphrag', 'index', '--root', './ragtest'])

    async def get_med_groups(self):
        return await self.report_generator.get_med_groups(f'medication used for {self.disorder}')

    async def get_med_names(self, med_group):
        return await self.report_generator.get_med_names(f'{med_group} for {self.disorder}')

    async def write_med_report(self, query) -> str:
        report = await self.report_generator.write_report(
            query,
            self.context
        )

        return report

    async def write_med_group_report(self, query) -> str:
        report = await self.report_generator.write_report(
            query,
            self.context
        )

        return report

