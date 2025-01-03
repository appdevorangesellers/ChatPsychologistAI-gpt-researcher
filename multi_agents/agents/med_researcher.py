from gpt_researcher import GPTMedResearcher
from colorama import Fore, Style
from .utils.views import print_agent_output
from typing import List, Dict, Set, Optional, Any
from gpt_researcher.actions import (
    generate_files,
)
import asyncio

class MedResearchAgent:
    def __init__(
        self,
        disorder: str
    ):
        self.disorder = disorder
        self.gpt_researcher = GPTMedResearcher(disorder=disorder)
        self.global_urls: Set[str] = set()

    async def research(self):
        await self._initial_research(f'medication used for {self.disorder}')
        med_groups = await self._get_med_groups()
        await self.construct_med_group_report(med_groups)
        await self.construct_med_report(med_groups)

    async def _initial_research(self, query) -> None:
        await self.gpt_researcher.conduct_context_research(query)
        self.global_urls = self.gpt_researcher.visited_urls

    async def _get_med_groups(self) -> List[Dict]:
        subtopics_data = await self.gpt_researcher.get_med_groups()

        all_subtopics = []
        if subtopics_data and subtopics_data.subtopics:
            for subtopic in subtopics_data.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {subtopics_data}")

        print("all_subtopics", all_subtopics)
        return all_subtopics

    async def construct_med_group_report(self, med_groups: List[Dict]):
        report_introduction = await self.gpt_researcher.write_introduction(f'medication used for {self.disorder}')
        print('report_introduction', report_introduction)
        _, report_body = await self._generate_med_group_sub_reports(med_groups)
        report = await self._construct_detailed_report(f'{self.disorder} medication', report_introduction,
                                                       report_body)
        print('report', report)

    async def construct_med_report(self, med_groups: List[Dict]):
        i = 1
        for topic in med_groups:
            await self._initial_research(f'{topic.get("task")} for {self.disorder}')
            med_names = await self._get_med_names(topic)
            report_introduction = await self.gpt_researcher.write_introduction(
                f'{topic.get("task")} for {self.disorder}')
            print('report_introduction', report_introduction)
            _, report_body = await self._generate_med_reports(med_names)
            report = await self._construct_detailed_report(f'{self.disorder} medication {topic}',
                                                           report_introduction, report_body)
            print('report', report)
            if i == 1: break
            i += 1

    async def _generate_med_group_sub_reports(self, subtopics: List[Dict]) -> tuple:
        subtopic_reports = []
        subtopics_report_body = ""

        for subtopic in subtopics:
            subtopic["task"] = f"{subtopic.get('task')} for {self.disorder}"
            result = await self._get_med_group_report(subtopic)
            if result["report"]:
                subtopic_reports.append(result)
                subtopics_report_body += f"\n\n\n{result['report']}"

        return subtopic_reports, subtopics_report_body

    async def _get_med_group_report(self, subtopic: Dict) -> Dict[str, str]:
        current_subtopic_task = subtopic.get("task")

        subtopic_report = await self.gpt_researcher.write_med_report(f'{current_subtopic_task}')

        return {"topic": subtopic, "report": subtopic_report}

    async def _get_med_names(self, query = None) -> List[Dict]:
        subtopics_data = await self.gpt_researcher.get_med_names(query)

        all_subtopics = []
        if subtopics_data and subtopics_data.subtopics:
            for subtopic in subtopics_data.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {subtopics_data}")

        print("_get_all_subtopics_2", all_subtopics)
        return all_subtopics

    async def _generate_med_reports(self, subtopics: List[Dict]) -> tuple:
        subtopic_reports = []
        subtopics_report_body = ""

        for subtopic in subtopics:
            result = await self._get_med_report(subtopic)
            if result["report"]:
                subtopic_reports.append(result)
                subtopics_report_body += f"\n\n\n{result['report']}"

        return subtopic_reports, subtopics_report_body

    async def _get_med_report(self, subtopic: Dict) -> Dict[str, str]:
        current_subtopic_task = subtopic.get("task")
        subtopic_assistant = GPTMedResearcher(report_type="subtopic_report")

        await subtopic_assistant.conduct_context_research(f'{current_subtopic_task} medication')
        self.global_urls.update(subtopic_assistant.visited_urls)

        subtopic_report = await subtopic_assistant.write_med_report(f'{current_subtopic_task}')

        return {"topic": subtopic, "report": subtopic_report}

    async def _construct_detailed_report(self, title, introduction: str, report_body: str) -> str:
        toc = self.gpt_researcher.table_of_contents(report_body)
        conclusion_with_references = self.gpt_researcher.add_references(
            '', self.global_urls)
        report = f"{introduction}\n\n{toc}\n\n{report_body}\n\n{conclusion_with_references}"
        await generate_files(report, title)
        return report