from gpt_researcher.utils.enum import Tone, ReportType
from .skills.topic_agent.writer import TopicReportGenerator
from .skills.topic_agent.researcher import TopicResearchConductor
from .config import Config

class GPTTopicWriter:
    def __init__(
        self,
        report_type: str = ReportType.SubtopicReport.value,
        tone: Tone = Tone.Objective,
        config_path="variables/default",
        subtopics: list = [],
        verbose: bool = True
    ):
        self.report_type = report_type
        self.tone = tone if isinstance(tone, Tone) else Tone.Objective
        self.websocket = None
        self.verbose = verbose
        self.role = "You are an experienced psychological assessment assistant. Your main task is to offer a comprehensive, insightful, and unbiased analysis of the provided information, offering general guidance based on psychological theories and frameworks."
        self.cfg = Config(config_path)
        self.research_conductor: TopicResearchConductor = TopicResearchConductor(self)
        self.report_generator: TopicReportGenerator = TopicReportGenerator(self)

    async def write_report(self, topic, topic_data) -> str:
        report = await self.report_generator.write_report(
            topic,
            topic_data
        )

        return report

    async def write_diagnoses(self, topic, topic_data):
        return await self.research_conductor.conduct_diagnoses_research(topic, topic_data)

    def add_costs(self, cost: float) -> None:
        return 0.0

    def get_costs(self) -> float:
        return 0.0