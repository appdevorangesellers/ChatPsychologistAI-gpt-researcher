from .agent import GPTResearcher
from .skills.sport_agent.writer import SportReportGenerator

from gpt_researcher.skills.sport_agent.researcher import SportResearchConductor
from .utils.enum import Tone, ReportType

class GPTSportResearcher(GPTResearcher):
    def __init__(
        self,
        symptom: str = "",
        report_type: str = ReportType.ResearchReport.value,
        tone: Tone = Tone.Objective,
        config_path="default",
        subtopics: list = [],
        websocket=None,
        verbose: bool = True
    ):
        super(GPTSportResearcher, self).__init__(report_type, tone, config_path, subtopics, websocket, verbose)
        self.symptom = symptom
        self.report_generator: SportReportGenerator = SportReportGenerator(self)
        self.research_conductor: SportResearchConductor = SportResearchConductor(self)

    async def conduct_research(self, query=None):
        print("GPTSportResearcher conduct_research")
        await self.research_conductor.conduct_research(self.get_summary_query())

    async def write_introduction(self, query=None):
        #await self._log_event("research", step="writing_introduction")
        intro = await super(GPTSportResearcher, self).write_introduction(self.get_summary_query())
        #await self._log_event("research", step="introduction_completed")
        return intro

    async def write_summary_report(self) -> str:
        report = await self.report_generator.write_report(
            self.get_summary_query(),
            self.context
        )

        return report

    def get_summary_query(self):
        return f'sport activities good for {self.symptom} associated with mental disorders'