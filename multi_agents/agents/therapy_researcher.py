from gpt_researcher import GPTTherapyResearcher
from colorama import Fore, Style
from .utils.views import print_agent_output
from typing import List, Dict, Set, Optional, Any
from gpt_researcher.actions import (
    generate_files,
)
import asyncio

class TherapyResearchAgent:
    def __init__(
        self,
        disorder: str
    ):
        self.disorder = disorder
        self.gpt_researcher = GPTTherapyResearcher(disorder=disorder)
        self.global_urls: Set[str] = set()

    async def research(self):
        await self._initial_research(f'therapies for {self.disorder}')
        therapies = await self._get_therapy_list()
        await self.construct_general_therapy_report(therapies)

    async def _initial_research(self, query) -> None:
        await self.gpt_researcher.conduct_research(query)
        self.global_urls = self.gpt_researcher.visited_urls

    async def _get_therapy_list(self) -> List[Dict]:
        therapies = await self.gpt_researcher.get_therapy_list()

        all_subtopics = []
        if therapies and therapies.subtopics:
            for subtopic in therapies.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {therapies}")

        print("all_subtopics", all_subtopics)
        return all_subtopics

    async def construct_general_therapy_report(self, therapies: List[Dict]):
        report_introduction = await self.gpt_researcher.write_introduction(f'therapies for {self.disorder}')
        print('report_introduction', report_introduction)
        _, report_body = await self._generate_therapy_sub_reports(therapies)
        report = await self._construct_detailed_report(f'{self.disorder} therapy', report_introduction,
                                                       report_body)
        print('report', report)

    async def _generate_therapy_sub_reports(self, subtopics: List[Dict]) -> tuple:
        subtopic_reports = []
        subtopics_report_body = ""

        for subtopic in subtopics:
            subtopic["task"] = f"{subtopic.get('task')} for {self.disorder}"
            print('subtopic["task"]', subtopic.get("task"))
            result = await self._get_therapy_report(subtopic)
            if result["report"]:
                subtopic_reports.append(result)
                subtopics_report_body += f"\n\n\n{result['report']}"

        return subtopic_reports, subtopics_report_body

    async def _get_therapy_report(self, subtopic: Dict) -> Dict[str, str]:
        current_subtopic_task = subtopic.get("task")

        subtopic_report = await self.gpt_researcher.write_general_therapy_report(f'{current_subtopic_task}')

        return {"topic": subtopic, "report": subtopic_report}

    async def _construct_detailed_report(self, title, introduction: str, report_body: str) -> str:
        toc = self.gpt_researcher.table_of_contents(report_body)
        conclusion_with_references = self.gpt_researcher.add_references(
            '', self.global_urls)
        report = f"{introduction}\n\n{toc}\n\n{report_body}\n\n{conclusion_with_references}"
        await generate_files(report, title)
        return report