from gpt_researcher import GPTSymptomResearcher, actions
from typing import Set

class SymptomResearchAgent:
    def __init__(
        self,
        disorder: str
    ):
        self.disorder = disorder
        self.gpt_researcher = GPTSymptomResearcher(disorder=disorder)
        self.global_urls: Set[str] = set()

    async def research(self):
        await self.gpt_researcher.conduct_research()
        report = await self.gpt_researcher.write_summary_report()
        await actions.generate_files(report, f"{self.disorder} symptoms")
